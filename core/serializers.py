from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Test, Section, Mcq, Subjective, RegisteredUser


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
    class Meta:
        model = Test
        fields = '__all__'
        extra_kwargs = {'created_by': {'read_only': True}}


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
