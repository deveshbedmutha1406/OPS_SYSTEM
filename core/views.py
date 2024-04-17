import os
import datetime
from .codesubmission import run_code
from .utils import add_cron_job, remove_cron_job
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .serializers import UserSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError
from .models import Test, Section, Mcq, Subjective, RegisteredUser, McqSubmission, SubjectiveSubmission, Coding, TestCases, CodingSubmission, Containers, SuspiciousImages, SuspiciousScore
from .serializers import TestSerializer, SectionSerializer, McqSerializer, SubjectiveSerializer, RegisterUserSerializer, \
    ListMcqSerializer, McqSubmissionSerializer, ListSubjectiveSerializer, SubjectiveSubmissionSerializer, CodingSerializer, TestCaseSerializer, CodingSubmissionSerializer, SuspiciousImagesSerializer, SuspiciousScoreSerializer
from .permissions import IsTestOwner, IsOtherThanOwner, IsRegisterForTest

class UserRegistration(generics.CreateAPIView):
    """Registers User"""
    queryset = User.objects.all()
    serializer_class = UserSerializer

class LoginUser(ObtainAuthToken):
    """Validate User Credentials And Return Token"""
    def post(self, request, *args, **kwargs):
        user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
        if user:
            # Try to get an existing token
            try:
                token = Token.objects.get(user=user)
            except Token.DoesNotExist:
                token = Token.objects.create(user=user)

            return Response({'token': token.key, 'user_id': token.user_id})
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_406_NOT_ACCEPTABLE)


class LogoutUser(generics.GenericAPIView):
    """Logs Out User And Deletes The Token"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        request.auth.delete()  # deleting existing token
        return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)


class TestListCreateView(generics.ListCreateAPIView):
    """Create and List Test Basic Information"""
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return Test.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TestDetailView(generics.RetrieveUpdateDestroyAPIView):
    """CRUD Operations on existing test's basic information"""
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    lookup_field = 'testid'

    def get_queryset(self):
        return Test.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SectionListView(generics.ListAPIView):
    serializer_class = SectionSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        testid = kwargs['testid']  # from url not query params
        try:
            objs = Section.objects.filter(test_id=testid)
        except:
            return Response({'detail': 'no section created'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(objs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SectionCreateView(generics.CreateAPIView):
    """Create section only by test admin also schedule cron job if coding question"""
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsTestOwner, IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def add_new_cron_job(self, exp, testid, flag):
        tmp = os.path.join(os.getcwd(), 'startScript.sh') if flag else os.path.join(os.getcwd(), 'endScript.sh')
        script_path = f'{tmp} {testid}'  # Example: path to your script file
        add_cron_job(exp, script_path)

    def perform_create(self, serializer):
        testObject = serializer.validated_data.get('test_id')
        if serializer.validated_data.get('qtype') == 'CODING':
            st_date = testObject.start_date - datetime.timedelta(minutes=1)
            en_date = testObject.end_date + datetime.timedelta(minutes=1)
            exp = f"{st_date.minute} {st_date.hour} {st_date.day} {st_date.month} *"
            end_exp = f"{en_date.minute} {en_date.hour} {en_date.day} {en_date.month} *"
            self.add_new_cron_job(exp, testObject.testid, True)  # add cron job for this test
            self.add_new_cron_job(end_exp, testObject.testid, False)
            for i in range(2):
                Containers.objects.get_or_create(test_id=testObject, container_name=f"container_{testObject.testid}_{i + 1}")
        serializer.save()


class SectionDestroyView(generics.DestroyAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsTestOwner, IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    lookup_field = 'sid'

    def perform_destroy(self, instance):
        qtype = instance.qtype
        testid = instance.test_id
        if qtype == 'MCQ':
            Mcq.objects.filter(test_id=testid).delete()
        elif qtype == 'CODING':
            Coding.objects.filter(test_id=testid).delete()
            # remove cron jobs.
            tmp = os.path.join(os.getcwd(), 'startScript.sh')
            tmp2 = os.path.join(os.getcwd(), 'endScript.sh')
            commands = [f"{tmp} {testid.testid}", f"{tmp2} {testid.testid}"]
            remove_cron_job(commands)
        else:
            Subjective.objects.filter(test_id=testid).delete()
        instance.delete()



class McqListCreateView(generics.ListCreateAPIView):
    """Creating And Listing Mcq for specific test"""
    serializer_class = McqSerializer
    permission_classes = [IsAuthenticated, IsTestOwner]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        testid = self.request.query_params.get('testid', None)
        print(testid)
        return Mcq.objects.filter(test_id=testid)

    def perform_create(self, serializer):
        testObject = serializer.validated_data.get('test_id')
        try:
            Section.objects.get(test_id=testObject, qtype='MCQ')
            serializer.save(settersid=self.request.user)
        except:
            raise ValidationError('Section does not exists')


class McqDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Crud operations on mcq which is created for specific test"""
    queryset = Mcq.objects.all()
    serializer_class = McqSerializer
    permission_classes = [IsTestOwner, IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        testid = self.request.data['test_id']
        return Mcq.objects.filter(test_id=testid)


class SubjectListCreateView(generics.ListCreateAPIView):
    serializer_class = SubjectiveSerializer
    permission_classes = [IsTestOwner, IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        testid = self.request.query_params.get('testid', None)
        return Subjective.objects.filter(test_id=testid)

    def perform_create(self, serializer):
        serializer.save(setters_id=self.request.user)


class SubjectiveDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subjective.objects.all()
    serializer_class = SubjectiveSerializer
    permission_classes = [IsTestOwner, IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        testid = self.request.data['test_id']
        return Subjective.objects.filter(test_id=testid)


class RegisterUserTest(generics.CreateAPIView, generics.RetrieveAPIView):
    """Register user for test other than owner
    This view stores user's face embedding along with testid which they are registered
    """
    serializer_class = RegisterUserSerializer
    permission_classes = [IsAuthenticated, IsOtherThanOwner]
    authentication_classes = [TokenAuthentication]

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)

    def get(self, request, *args, **kwargs):
        test_id = kwargs.get('testid', None)
        if test_id is None:
            return Response({'error': 'testid not provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            test_instance = Test.objects.get(testid=test_id)
        except:
            return Response({'error': 'invalid test id provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user_data = RegisteredUser.objects.get(user_id=request.user, test_id=test_instance)
        except:
            return Response({'error': f"User Not Registered"}, status=status.HTTP_404_NOT_FOUND)

        return Response(self.serializer_class(user_data).data, status=status.HTTP_200_OK)


class GetMcqQuestions(generics.ListAPIView):
    """Endpoint for displaying question during the test"""
    serializer_class = ListMcqSerializer
    permission_classes = [IsAuthenticated, IsRegisterForTest]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        testid = self.kwargs.get('testid', None)
        return Mcq.objects.filter(test_id=testid)


class SubmitMcq(generics.ListCreateAPIView):
    """Accepting Submission for mcq"""
    serializer_class = McqSubmissionSerializer
    permission_classes = [IsAuthenticated, IsRegisterForTest]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        testid = self.kwargs.get('testid', None)
        return McqSubmission.objects.filter(test_id=testid, user_id=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data
        # check if already submission exists.
        try:
            sub_instance = McqSubmission.objects.get(user_id=request.user, ques_id=validated.get('ques_id'),
                                                     test_id=validated.get('test_id'))
            sub_instance.marked_option = validated.get('marked_option')
            sub_instance.save()
            return Response(self.serializer_class(sub_instance).data, status=status.HTTP_201_CREATED)
        except:
            # not exist before so create one
            serializer.save(user_id=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class GetSubjectiveQuestions(generics.ListAPIView):
    """View for displaying subjective questions during test"""
    serializer_class = ListSubjectiveSerializer
    permission_classes = [IsAuthenticated, IsRegisterForTest]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        testid = self.kwargs.get('testid', None)
        return Subjective.objects.filter(test_id=testid)


class SubmitSubjective(generics.ListCreateAPIView):
    """Modifying existing submission for subjective questions"""
    serializer_class = SubjectiveSubmissionSerializer
    permission_classes = [IsAuthenticated, IsRegisterForTest]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        testid = self.kwargs.get('testid', None)  # get from url
        return SubjectiveSubmission.objects.filter(test_id=testid, user_id=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data
        print(validated)
        try:
            sub_instance = SubjectiveSubmission.objects.get(user_id=request.user, ques_id=validated.get('ques_id'),
                                                            test_id=validated.get('test_id'))
            sub_instance.submitted_answer = validated.get('submitted_answer')
            print(sub_instance)
            sub_instance.save()
            return Response(self.serializer_class(sub_instance).data, status=status.HTTP_201_CREATED)
        except:
            # not exist before so create one
            serializer.save(user_id=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class getAllTests(generics.ListAPIView):
    """Return all test for general dashboard which are not created by other user's"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TestSerializer

    def get_queryset(self):
        return Test.objects.exclude(created_by=self.request.user)


class CodingListCreateView(generics.ListCreateAPIView):
    """Creating And Listing Coding for specific test"""
    serializer_class = CodingSerializer
    permission_classes = [IsAuthenticated, IsTestOwner]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        testid = self.request.query_params.get('testid', None)
        return Coding.objects.filter(test_id=testid)

    def perform_create(self, serializer):
        testObject = serializer.validated_data.get('test_id')
        try:
            Section.objects.get(test_id=testObject, qtype='CODING')
            serializer.save(settersid=self.request.user)
        except:
            raise ValidationError('Section does not exists')


class CodingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Crud operations on Coding which is created for specific test"""
    queryset = Coding.objects.all()
    serializer_class = CodingSerializer
    permission_classes = [IsTestOwner, IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        testid = self.request.data['test_id']
        return Coding.objects.filter(test_id=testid)


class TestCaseListCreateView(generics.ListCreateAPIView):
    serializer_class = TestCaseSerializer
    permission_classes = [IsTestOwner, IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        testid = self.request.query_params.get('testid', None)
        return TestCases.objects.filter(test_id=testid)

    def perform_create(self, serializer):
        quesObject = serializer.validated_data.get('q_id')
        try:
            Coding.objects.get(qid=quesObject.qid)
            serializer.save()
        except:
            raise ValidationError('Question does not exists')

class TestCaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TestCaseSerializer
    permission_classes = [IsTestOwner, IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        testid = self.request.data['test_id']
        return TestCases.objects.filter(test_id=testid)

    def perform_destroy(self, instance):
        # Get the paths of the files associated with the TestCases instance
        input_file_path = instance.tc_input.path
        output_file_path = instance.tc_output.path

        # Delete the files from the filesystem
        if os.path.exists(input_file_path):
            os.remove(input_file_path)
        if os.path.exists(output_file_path):
            os.remove(output_file_path)

        # Delete the database instance
        instance.delete()


class CodingSubmissionView(generics.ListCreateAPIView):
    serializer_class = CodingSubmissionSerializer
    permission_classes = [IsRegisterForTest, IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        var = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(var, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        customInput = self.request.data['customInput']
        data = serializer.validated_data
        code = data.get('code')
        lang = data.get('lang')
        test_id = data.get('test_id').testid
        ques_id = data.get('ques_id').qid
        var = run_code(code, lang, test_id, ques_id, customInput)
        serializer.save(user_id=self.request.user, status=var['returnCode'])
        return var



class GetCodingQuestions(generics.ListCreateAPIView):
    """Listing Coding for specific test During Test"""
    serializer_class = CodingSerializer
    permission_classes = [IsAuthenticated, IsRegisterForTest]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        testid = self.kwargs.get('testid', None)
        return Coding.objects.filter(test_id=testid)

class UploadSusImages(generics.ListCreateAPIView):
    serializer_class = SuspiciousImagesSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        testid = self.kwargs.get('testid', None)
        userid = self.request.query_params.get('uid', None)
        print(userid, testid)
        return SuspiciousImages.objects.filter(test_id=testid, user_id=userid)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)

class UpdateSusScore(generics.ListCreateAPIView):
    serializer_class = SuspiciousScoreSerializer
    permission_classes = [IsAuthenticated, IsRegisterForTest]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        testid = self.kwargs.get('testid', None)
        userid = self.kwargs.get('userid', None)
        return SuspiciousScore.objects.filter(test_id=testid, user_id=userid)

    def perform_create(self, serializer):
        testid = self.kwargs.get('testid', None)
        userid = self.kwargs.get('userid', None)
        
        existing_object = SuspiciousScore.objects.filter(test_id=testid, user_id=self.request.user).first()
        if existing_object:
            existing_object.tab_switch_count = existing_object.tab_switch_count + 1
            existing_object.save()
        else:
            serializer.save(user_id=self.request.user)

class getRegisteredUserForTest(generics.ListAPIView):
    serializer_class = RegisterUserSerializer
    permission_classes = [IsAuthenticated, IsTestOwner]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        testid = self.kwargs.get('testid', None)
        return RegisteredUser.objects.filter(test_id=testid)


class getMcqScore(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsTestOwner]
    authentication_classes = [TokenAuthentication]
    def get(self, request, *args, **kwargs):
        testid = self.kwargs.get('testid', None)
        userid = self.kwargs.get('userid', None)
        McqQues = Mcq.objects.filter(test_id=testid).values('qid', 'correct_option')
        McqSubs = McqSubmission.objects.filter(test_id=testid, user_id=userid).values('ques_id', 'marked_option')
        key_map = {ele['qid']: ele['correct_option'] for ele in McqQues}
        score = 0
        for ele in McqSubs:
            if ele['ques_id'] in key_map:
                if ele['marked_option'] == key_map[ele['ques_id']]:
                    score += 1
        return Response({'score': score}, status=status.HTTP_200_OK)
