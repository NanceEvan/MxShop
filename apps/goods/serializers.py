#!/usr/bin/python  
# -*- coding:utf-8 _*-
""" 
@author: Sizer
@contact: 591207060@qq.com 
@software: PyCharm 
@file: serializer 
@time: 2019/2/12 13:20 
"""
from django.db.models import Q
from rest_framework import serializers

from goods.models import Goods, GoodsCategory, PriceRange, GoodsImage, Banner, GoodsCategoryBrand, IndexAd, \
    HotSearchWords


class HotSearchWordsSerializer(serializers.ModelSerializer):
    """
        搜索热词
    """

    class Meta:
        model = HotSearchWords
        fields = '__all__'


class GoodsImageSerializer(serializers.ModelSerializer):
    """
        轮播图
    """

    class Meta:
        model = GoodsImage
        fields = ('image',)


class SubCatSerializer2(serializers.ModelSerializer):
    """
        商品三级分类序列化
    """

    class Meta:
        model = GoodsCategory
        fields = "__all__"


class SubCatSerializer(serializers.ModelSerializer):
    """
        商品二级分类序列化
    """
    sub_cat = SubCatSerializer2(many=True)

    class Meta:
        model = GoodsCategory
        fields = "__all__"


class GoodsCategorySerializer(serializers.ModelSerializer):
    """
        商品一级分类序列化
    """
    sub_cat = SubCatSerializer(many=True)

    class Meta:
        model = GoodsCategory
        fields = "__all__"


class GoodsSerializer(serializers.ModelSerializer):
    """
        商品序列化
    """
    category = GoodsCategorySerializer()
    # images是数据库中设置的related_name=images， 把轮播图嵌套进来
    images = GoodsImageSerializer(many=True)

    class Meta:
        model = Goods
        fields = "__all__"


class PriceRangeSerializer(serializers.ModelSerializer):
    """
        价格区间分类序列化
    """

    class Meta:
        model = PriceRange
        fields = "__all__"


class BannerSerializer(serializers.ModelSerializer):
    """
        轮播图
    """
    class Meta:
        model = Banner
        fields = '__all__'


class BrandSerializer(serializers.ModelSerializer):
    """
        大类下面的宣传图标
    """
    class Meta:
        model = GoodsCategoryBrand
        fields = '__all__'


class IndexCategorySerializer(serializers.ModelSerializer):
    # 某个大类的商标， 可以有多个商标， 属于一对多的关系
    brands = BrandSerializer(many=True)
    # good有一个外键category， 但这个外键指向的是三级类， 直接反向通过category（三级类）， 取某个大类下的商品是取不出来的
    goods = serializers.SerializerMethodField()
    # 在parent_category字段中定义的related_name='sub_cat'
    # 取二级商品分类
    sub_cat = SubCatSerializer(many=True)
    # 广告商品
    ad_goods = serializers.SerializerMethodField()

    def get_ad_goods(self, obj):
        goods_json = {}
        ad_goods = IndexAd.objects.filter(category_id=obj.id)
        if ad_goods:
            # 取这个的商品QuerySet[0]
            # 每个category的indexad只有yige
            goods_ins = ad_goods[0].goods
            # 在serializer里面调用serializer的话， 就要添加一个参数context（上下文request）， 嵌套serializer必须家
            # serializer返回的时候一定加'.data' 这样返回的才是json数据
            goods_json = GoodsSerializer(goods_ins, many=False, context={'request': self.context['request']}).data
        return goods_json

    def get_goods(self, obj):
        # 将这个商品相关父类子类等都可以进行匹配
        all_goods = Goods.objects.filter(Q(category_id=obj.id) | Q(category__parent_category_id=obj.id) |
                                         Q(category__parent_category__parent_category_id=obj.id))
        goods_serializer = GoodsSerializer(all_goods, many=True, context={'request': self.context['request']})
        return goods_serializer.data

    class Meta:
        model = GoodsCategory
        fields = '__all__'
