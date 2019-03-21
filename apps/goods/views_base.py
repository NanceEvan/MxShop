#!/usr/bin/python  
# -*- coding:utf-8 _*-
""" 
@author: Sizer
@contact: 591207060@qq.com 
@software: PyCharm 
@file: views_base 
@time: 2019/2/12 11:38 
"""
from django.http import JsonResponse
from django.views.generic.base import View

from goods.models import Goods


class GoodsListView(View):
    def get(self, request):
        """
            通过django的view实现商品列表页
        :param request:
        :return:
        """
        json_list = []
        goods = Goods.objects.all()[:10]
        # for good in goods:
        #     json_dict = {
        #         'name': good.name,
        #         'category': good.category.name,
        #         'market_price': good.market_price,
        #         'add_time': good.add_time
        #     }
        #     json_list.append(json_dict)

        # from django.forms.models import model_to_dict
        # for good in goods:
        #     json_dict = model_to_dict(good)
        #     json_list.append(json_dict)

        import json
        from django.core import serializers
        from django.http import HttpResponse

        # type(goods) <class 'django.db.models.query.QuerySet'>
        # type(json_data) <class 'str'>
        json_data = serializers.serialize("json", goods)
        # type(json_data) <class 'list'>
        json_data = json.loads(json_data)
        # return HttpResponse(json.dumps(json_list), content_type='application/json')
        # return HttpResponse(json_data, content_type='application/json')
        return JsonResponse(json_data, safe=False)
