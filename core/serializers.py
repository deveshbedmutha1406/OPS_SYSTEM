from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Test, Section, Mcq, Subjective, RegisteredUser, McqSubmission, SubjectiveSubmission


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # to make password hashed.
        user.save()
        Token.objects.create(user=user)
        return user


class TestSerializer(serializers.ModelSerializer):
    sections = serializers.SerializerMethodField()
    class Meta:
        model = Test
        fields = ['testid', 'created_by', 'title', 'description','start_date','end_date','sections']
        extra_kwargs = {'created_by': {'read_only': True}}

    def get_sections(self, obj):
        l1 = []
        for obj in Section.objects.filter(test_id=obj.testid):
            l1.append({"qtype": obj.qtype,"sid": obj.sid})
        return l1


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'


class McqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mcq
        fields = '__all__'
        extra_kwargs = {'settersid': {'read_only': True}}


class SubjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjective
        fields = '__all__'
        extra_kwargs = {'setters_id': {'read_only': True}}


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisteredUser
        fields = '__all__'
        extra_kwargs = {'user_id': {'read_only': True}}


class ListMcqSerializer(serializers.ModelSerializer):
    marked_option = serializers.SerializerMethodField()

    class Meta:
        model = Mcq
        fields = ['qid', 'test_id', 'qno', 'question_text', 'optionA', 'optionB', 'optionC', 'optionD', 'marked_option']

    def get_marked_option(self, obj):
        try:
            obj = McqSubmission.objects.get(
                test_id=obj.test_id,
                user_id=self.context['request'].user,
                ques_id=obj.qid
            )
            return obj.marked_option
        except:
            return None

class McqSubmissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = McqSubmission
        fields = '__all__'
        extra_kwargs = {'user_id': {'read_only': True}}


class ListSubjectiveSerializer(serializers.ModelSerializer):
    submitted_ans = serializers.SerializerMethodField()
    class Meta:
        model = Subjective
        fields = ['qid', 'test_id', 'statement', 'submitted_ans']

    def get_submitted_ans(self, obj):
        try:
            obj = SubjectiveSubmission.objects.get(
                test_id=obj.test_id,
                user_id=self.context['request'].user,
                ques_id=obj.qid
            )
            return obj.submitted_answer
        except:
            return None

class SubjectiveSubmissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubjectiveSubmission
        fields = '__all__'
        extra_kwargs = {'user_id': {'read_only': True}}
