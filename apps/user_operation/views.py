import random

from django.shortcuts import render
from django.core.mail import send_mail
from rest_framework import mixins, status
from rest_framework import viewsets

# Create your views here.
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from user_operation.models import UserFav, UserMessage, UserAddress
from user_operation.serializers import UserFavSerializer, UserFavDetailSerializer, UserMessageSerializer, \
    AddressSerializer
from users.models import VerifyCode
from users.serializers import VerifyCodeSerializer
from utils.permissions import IsOwnerOrReadOnly
from utils.verify_code import send_code_email


class VerifyCodeViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
        create:
            生成验证码
    """
    queryset = VerifyCode.objects.all()
    serializer_class = VerifyCodeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        try:
            code = send_code_email(email, 'register')
            return Response({
                'email': email,
                'code': code
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'email': email,
                'msg': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserFavViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """
        list:
            用户收藏情况
        create:
            收藏商品
        destroy:
            取消收藏商品
    """
    queryset = UserFav.objects.all()
    serializer_class = UserFavSerializer
    # permission是用来做权限判断的
    # IsAuthenticated: 必须登录用户， IsOwnerOrReadOnly： 必须是当前登录的用户
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    # auth 用来做用户认证，
    # 因为已经在setting中去掉了全局认证， 所以在此添加认证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    # 搜索的字段
    lookup_field = 'goods_id'

    def get_queryset(self):
        # 只能查看当前登录用户的收藏， 不会获取所有用户的收藏
        return UserFav.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return UserFavDetailSerializer
        # elif self.action == "create":
        else:
            return UserFavSerializer


class UserMessageViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
        list:
           获取用户留言
        create：
            添加留言
        delete:
            删除留言
    """
    queryset = UserMessage.objects.all()
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = UserMessageSerializer

    def get_queryset(self):
        # 用户只能看到自己的留言
        return UserMessage.objects.filter(user=self.request.user)


class UserAddressViewSet(viewsets.ModelViewSet):
    """
        收货地址管理
        list：
            获取收货地址
        create：
            添加收货地址
        update：
            更新收货地址
        delete：
            删除收货地址
    """
    queryset = UserAddress.objects.all()
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = AddressSerializer

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)
