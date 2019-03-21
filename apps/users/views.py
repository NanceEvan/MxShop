from django.shortcuts import render

# Create your views here.
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import mixins, viewsets, status, authentication, permissions
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from users.models import UserProfile
from users.serializers import UsersRegisterSerializer, UserDetailSerializer

User = get_user_model()


class CustomBackend(ModelBackend):
    """
    自定义用户验证
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 用户名和手机都能登录
            user = User.objects.get(
                Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class UsersViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
        create:
            用户注册
        retrieve:
            获取用户details
    """
    queryset = UserProfile.objects.all().order_by('id')
    serializer_class = UsersRegisterSerializer

    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        re_dict = serializer.data
        payload = jwt_payload_handler(user)

        re_dict["token"] = jwt_encode_handler(payload)
        re_dict["name"] = user.name if user.name else user.username

        headers = self.get_success_headers(serializer.data)

        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    # 这里需要动态权限配置
    # 1、用户注册的时候不需要权限限制
    # 2、获取用户详情信息的时候需要用户登陆
    def get_permissions(self):
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated()]
        elif self.action == 'create':
            return []
        return []

    # 动态选择Serializer
    # 用户注册只返回username 和 mobile， 会员中心页面需要显示更多字段，所以需要出啊过年就爱你UserDetailSerializer
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action == 'create':
            return UsersRegisterSerializer
        return UserDetailSerializer

    # 虽然继承了Retrieve可以获取用户详情， 但是并不知道用户的id， 所有要重写get_object方法
    # 在前端页面的逻辑中并不会知道当前用户的id， 所以需要通过drf的request中user（也就是通过session中jwt的方式）获取user
    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        return serializer.save()
