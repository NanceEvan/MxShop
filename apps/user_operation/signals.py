#!/usr/bin/python  
# -*- coding:utf-8 _*-
""" 
@author: sizer
@contact: 591207060@qq.com 
@software: PyCharm 
@file: signal
@time: 2019-02-27 12:27
"""

# post_save： 接受信号量的方式
# sender 接受信号量的model
from django.core.signals import request_started
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from goods.models import Goods
from goods.views import GoodsListViewSet
from user_operation.models import UserFav


@receiver(post_save, sender=UserFav)
def create_UserFav(sender, instance=None, created=False, **kwargs):
    """
        商品收藏信号量增加
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    # 是否新建， 因为update的时候也会进行post_save
    if created:
        goods = instance.goods
        goods.fav_num += 1
        goods.save()


@receiver(post_delete, sender=UserFav)
def delete_UserFav(sender, instance=None, created=False, **kwargs):
    """
        商品取消收藏信号量减少
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    goods = instance.goods
    goods.fav_num -= 1
    goods.save()

@receiver(request_started, sender=GoodsListViewSet)
def click_GoodsDetail(sender, instance=None, created=False, **kwargs):
    """
        点击商品详情增加点击数
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    pass
