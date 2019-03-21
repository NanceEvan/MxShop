#!/usr/bin/python  
# -*- coding:utf-8 _*-
""" 
@author: Sizer
@contact: 591207060@qq.com 
@software: PyCharm 
@file: serializers 
@time: 2019/2/14 14:06 
"""
import re
from datetime import datetime, timedelta

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import UserProfile, VerifyCode


class UsersRegisterSerializer(serializers.ModelSerializer):
    """
        用户注册序列化
    """
    # UserProfile 中没有code字段，需要自定义一个code序列化字段
    code = serializers.CharField(required=True, write_only=True, max_length=6, min_length=6,
                                 error_messages={
                                     'black': '请输入验证码',
                                     'required': '请输入验证码',
                                     'max_length': '验证码格式错误',
                                     'min_length': '验证码格式错误'
                                 }, help_text='验证码')
    # password 在注册时需要password信息， 但注册完成之后不需要返回给用户password信息
    password = serializers.CharField(
        style={'input_type': 'password'}, label='password',
        write_only=True, required=True, help_text='密码'
    )
    # 验证用户名是否存在
    email = serializers.CharField(
        label='email', help_text='email', required=True, allow_blank=False,
        validators=[UniqueValidator(queryset=UserProfile.objects.all(), message="邮箱已经存在")]
    )

    # Field-level validation
    def validate_code(self, code):
        # 用户注册，已post方式提交注册信息，post的数据都保存在initial_data里面
        # username就是用户注册的手机号，验证码按添加时间倒序排序，为了后面验证过期，错误等
        verify_records = VerifyCode.objects.filter(email=self.initial_data["email"], send_type='register').order_by(
            "-add_time")

        if verify_records:
            # 最近的一个验证码
            last_record = verify_records[0]
            # 有效期为五分钟。
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_mintes_ago > last_record.add_time:
                raise serializers.ValidationError("验证码过期")

            if last_record.code != code:
                raise serializers.ValidationError("验证码错误")

        else:
            raise serializers.ValidationError("验证码错误")

        # 所有字段。attrs是字段验证合法之后返回的总的dict

    # Object-level validation
    def validate(self, attrs):
        # # 前端没有传email值到后端，这里添加进来
        attrs["username"] = attrs["email"]
        # code是自己添加得，数据库中并没有这个字段，验证完就删除掉
        del attrs["code"]
        return attrs

    class Meta:
        model = UserProfile
        fields = ('code', 'email', 'password')


class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100, help_text='email')

    # 函数名必须: validate + 验证字段名
    def validate_email(self, email):
        """
            邮箱字段验证
        :param email:
        :return:
        """
        # 是否已经存在
        if UserProfile.objects.filter(email=email):
            raise serializers.ValidationError('用户已经存在')

        # 验证码发送频率
        # 60s 内只能发送一次
        one_mintes_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if VerifyCode.objects.filter(add_time__gt=one_mintes_ago, email=email).count():
            raise serializers.ValidationError('距离上次发送未超过60s')

        return email


class UserDetailSerializer(serializers.ModelSerializer):
    """
        用户详情
    """
    class Meta:
        model = UserProfile
        fields = ("name", "gender", "birthday", "email", "mobile")
