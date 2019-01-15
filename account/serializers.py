from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from .models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        write_only_fields = ('password',)


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = UserProfile
        fields = ('nickname', 'user', 'activate_key', 'activate_key_expires')

    def create(self, validated_data):
        with transaction.atomic():
            user_data = validated_data.pop('user')
            user = User.objects.create_user(**user_data)
            # when is_active is False, user can not login. User will be active until verify email.
            user.is_active = False
            user.save()
            userprofile = UserProfile.objects.create(user=user, **validated_data)
            return userprofile


class AccountOperate():
    def __init__(self, operate, success, info=None, redirect_url=None):
        self.operate = operate
        self.success = success
        self.info = info
        self.redirect_url = redirect_url


class AccountOperateSerializer(serializers.Serializer):
    operate = serializers.CharField(max_length=20, required=True)
    success = serializers.BooleanField(required=True)
    info = serializers.CharField(max_length=100, required=False)
    redirect_url = serializers.CharField(max_length=300, required=False)

    def create(self, validated_data):
        return AccountOperate(**validated_data)
