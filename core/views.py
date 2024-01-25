from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .serializers import UserSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication


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

    def post(self, request, *args, **kwargs):
        request.auth.delete()
        return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)

