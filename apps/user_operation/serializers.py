#!/usr/bin/python  
# -*- coding:utf-8 _*-
""" 
@author: Sizer
@contact: 591207060@qq.com 
@software: PyCharm 
@file: serializer 
@time: 2019/2/14 11:57 
"""
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from goods.serializers import GoodsSerializer
from user_operation.models import UserFav, UserMessage, UserAddress


class UserFavSerializer(serializers.ModelSerializer):
    # 获取当前登录的用户
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        # validate实现唯一联合，一个商品只能收藏一次
        validators = [
            UniqueTogetherValidator(
                queryset=UserFav.objects.all(),
                fields=('user', 'goods'),
                # message的信息可以自定义
                message="已经收藏"
            )
        ]
        model = UserFav
        # 收藏的时候需要返回商品的id，因为取消收藏的时候必须知道商品的id是多少
        fields = ("user", "goods", 'id')


class UserFavDetailSerializer(serializers.ModelSerializer):
    """
        用户收藏详情
    """
    goods = GoodsSerializer()

    class Meta:
        model = UserFav
        fields = ("goods", "id")


class UserMessageSerializer(serializers.ModelSerializer):
    """
        用户留言
    """
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    add_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")
    file = serializers.FileField(allow_empty_file=True, allow_null=True, required=False)

    class Meta:
        model = UserMessage
        fields = ['user', 'message_type', 'subject', 'message', 'file', 'id', 'add_time']


class AddressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    id = serializers.IntegerField(read_only=True)
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')
    province = serializers.CharField(max_length=100, required=True)
    city = serializers.CharField(max_length=100, required=True)
    district = serializers.CharField(max_length=100, required=True)
    address = serializers.CharField(max_length=100, required=True)
    signer_name = serializers.CharField(max_length=100, required=True)
    signer_mobile = serializers.CharField(max_length=11, required=True)

    class Meta:
        model = UserAddress
        fields = ('id', 'user', 'province', 'city', 'district', 'address', 'signer_name', 'signer_mobile', 'add_time',)

