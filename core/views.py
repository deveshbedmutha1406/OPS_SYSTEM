from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .serializers import UserSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from .models import Test, Section, Mcq
from .serializers import TestSerializer, SectionSerializer, McqSerializer
from .permissions import IsTestOwner
import json

class UserRegistration(generics.CreateAPIView):
    """Registers User"""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LoginUser(ObtainAuthToken):
    """Validate User Credentials And Return Token"""
    def post(self, request, *args, **kwargs):
        print(request.data.get('password'))
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
        request.auth.delete()
        return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)


class TestListCreateView(generics.ListCreateAPIView):
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return Test.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TestDetailView(generics.RetrieveUpdateDestroyAPIView):
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
    permission_classes = [IsTestOwner, IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        testid = kwargs['testid']
        try:
            objs = Section.objects.filter(test_id=testid)
        except:
            return Response({'detail': 'no section created'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(objs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SectionCreateView(generics.CreateAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsTestOwner, IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class SectionDestroyView(generics.DestroyAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsTestOwner, IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    lookup_field = 'sid'


class McqListCreateView(generics.ListCreateAPIView):
    serializer_class = McqSerializer
    permission_classes = [IsAuthenticated, IsTestOwner]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        testid = self.request.data['test_id']
        return Mcq.objects.filter(test_id=testid)

    def perform_create(self, serializer):
        serializer.save(settersid=self.request.user)


class McqDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Mcq.objects.all()
    serializer_class = McqSerializer
    permission_classes = [IsTestOwner, IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        testid = self.request.data['test_id']
        return Mcq.objects.filter(test_id=testid)