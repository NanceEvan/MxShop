from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework import mixins
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from goods.exceptions import GoodsInventoryShortageException
from trade.models import ShopCart, OrderInfo, OrderGoods
from trade.serializers import ShopCartSerializer, ShopCartDetailSerializer, OrderSerializer, OrderDetailSerializer
from utils.permissions import IsOwnerOrReadOnly


class ShopCartViewSet(viewsets.ModelViewSet):
    """
    购物车功能
    list:
        获取购物车详情
    create:
        加入购物车
    delete：
        删除购物车
    """
    lookup_field = 'goods_id'
    queryset = ShopCart.objects.all()
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    serializer_class = ShopCartSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 如果已经没有库存返回
        try:
            self.perform_create(serializer)
        except GoodsInventoryShortageException:
            return Response(data={'error': '商品已经没有足够的库存'}, status=status.HTTP_403_FORBIDDEN, exception=True)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_update(serializer)
        except GoodsInventoryShortageException:
            return Response(data={'error': '商品已经没有足够的库存'}, status=status.HTTP_403_FORBIDDEN, exception=True)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_create(self, serializer):
        shop_cart = serializer.save()
        goods = shop_cart.goods
        if goods.goods_num - shop_cart.nums < 0:
            raise GoodsInventoryShortageException
        goods.goods_num -= shop_cart.nums
        goods.save()

    def perform_destroy(self, instance):
        goods = instance.goods
        goods.goods_num += instance.nums
        goods.save()
        instance.delete()

    def perform_update(self, serializer):
        # 首先获取修改之前的库存数量
        existed_record = ShopCart.objects.get(id=serializer.id)
        existed_nums = existed_record.nums
        # 先保存之前的数据
        saved_record = serializer.save()
        # 变化的数量
        nums = saved_record.nums - existed_nums
        goods = saved_record.goods
        if goods.goods_num - nums < 0:
            raise GoodsInventoryShortageException
        goods.goods_num -= nums
        goods.save()

    def get_queryset(self):
        return ShopCart.objects.filter(user=self.request.user)

    # 设置动态serializer
    def get_serializer_class(self):
        if self.action == 'list':
            return ShopCartDetailSerializer
        else:
            return ShopCartSerializer


class OrderViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.CreateModelMixin,
                   viewsets.GenericViewSet):

    queryset = OrderInfo.objects.all()
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = OrderSerializer

    # 动态配置serializer
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderSerializer

    # 获取订单列表
    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

    # 在订单提交保存之前还需要多两步步骤， 所以这里自定义perform_create()方法
    # 1、将购物车中的商品保存到OrderGoods中
    # 2、清空购物车
    def perform_create(self, serializer):
        order = serializer.save()
        # 获取购物车中所有商品
        shop_carts = ShopCart.objects.filter(user=self.request.user)
        for shop_cart in shop_carts:
            order_goods = OrderGoods(goods=shop_cart.goods, goods_num=shop_cart.nums, order=order)
            order_goods.save()
            # 清空购物车
            shop_cart.delete()

        return order


