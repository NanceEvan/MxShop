#!/usr/bin/python  
# -*- coding:utf-8 _*-
""" 
@author: sizer
@contact: 591207060@qq.com 
@software: PyCharm 
@file: signals
@time: 2019-02-27 18:58
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from trade.models import ShopCart


# @receiver(post_save, sender=ShopCart)
# def create_ShopCart(sender, instance=None, created=False, **kwargs):
#     """
#         新建购物车
#     :param sender:
#     :param instance:
#     :param created:
#     :param kwargs:
#     :return:
#     """
#
#     if created:
#         # 如果是新增商品购物车
#         goods = instance.goods
#
#         if goods.goods_num - instance.nums < 0:
#             pass
#         else:
#             goods.goods_num -= instance.nums
#             goods.save()