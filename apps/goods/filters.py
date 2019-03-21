#!/usr/bin/python  
# -*- coding:utf-8 _*-
""" 
@author: Sizer
@contact: 591207060@qq.com 
@software: PyCharm 
@file: filters 
@time: 2019/2/12 16:11 
"""
from django.db.models import Q
from django_filters import rest_framework as filters

from goods.models import Goods


class GoodsFilter(filters.FilterSet):
    pricemin = filters.NumberFilter(field_name="shop_price", lookup_expr='gte')
    pricemax = filters.NumberFilter(field_name="shop_price", lookup_expr='lte')
    # name 模糊查询  前置i表示忽略大小写
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    top_category = filters.NumberFilter(field_name='category', method='top_category_filter')

    def top_category_filter(self, queryset, name, value):
        return queryset.filter(Q(category_id=value) |
                               Q(category__parent_category_id=value) |
                               Q(category__parent_category__parent_category_id=value)
                                )

    class Meta:
        model = Goods
        fields = ['name', 'pricemin', 'pricemax', 'is_hot', 'is_new']
