import time
from random import Random

from rest_framework import serializers

from goods.models import Goods
from trade.models import ShopCart, OrderGoods, OrderInfo
from goods.serializers import GoodsSerializer


class ShopCartDetailSerializer(serializers.ModelSerializer):
    # 一个ShopCart对应一个goods
    goods = GoodsSerializer(many=False)

    class Meta:
        model = ShopCart
        fields = '__all__'


class ShopCartSerializer(serializers.Serializer):
    # 如果使用ModelSerializer
    # 在CreateModelMixin中调用create方法的时候，
    # 运行到serializer.is_vaild(raise_exception=True)的时候就会报错
    # 而serializer的save则是在self.perform_create(serializer)中调用，
    # 所以使用ModelSerializer的时候， 即使是重写serializer的create仍然无法通过验证

    # 如果不使用serializer而是自己实现模拟serializer的操作，
    # 会导致代码的分离性和重用性不高， 并且无法生成文档

    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    nums = serializers.IntegerField(required=True, min_value=1,
                                    error_messages={
                                        'min_value': '商品数量不能小于1',
                                        'required': '请选择购买数量'
                                    })
    # 此处继承Serializer， 必须指定queryset对象， 如果继承ModelSerializer则不需要指定
    # goods是一个外键， 可以通过这种方法获取goods object中所有的值
    goods = serializers.PrimaryKeyRelatedField(required=True, queryset=Goods.objects.all())
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    # 继承的Serializer没有save功能， 必须重写一个create方法
    def create(self, validated_data):
        # validated_data是已经调用is_valid()处理过的数据
        # 获取当前用户
        # view中 self.request.user
        # serializer中  self.context['request'].user
        user = self.context['request'].user
        nums = validated_data['nums']
        goods = validated_data['goods']

        existed = ShopCart.objects.filter(user=user, goods=goods)
        if existed:
            # 如果购物车中有记录， 增加数量
            existed = existed[0]
            existed.nums += nums
            existed.save()
        else:
            # 如果购物车中没有记录， 则创建
            existed = ShopCart.objects.create(**validated_data)

        return existed

    def update(self, instance, validated_data):
        # 保证传递过来的需要修改的商品和instance是同一商品
        if instance.goods_id == validated_data['goods'].id:
            # 修改商品数量
            instance.nums = validated_data['nums']
            instance.save()
        return instance


class OrderGoodsSerialzier(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)

    class Meta:
        model = OrderGoods
        fields = "__all__"


class OrderDetailSerializer(serializers.ModelSerializer):
    goods = OrderGoodsSerialzier(many=True)
    post_script = serializers.CharField(required=False)

    class Meta:
        model = OrderInfo
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    # 生成订单的时候， 这些信息不需要post
    pay_status = serializers.CharField(read_only=True)
    trade_no = serializers.CharField(read_only=True)
    order_sn = serializers.CharField(read_only=True)
    pay_time = serializers.DateTimeField(read_only=True)
    nonce_str = serializers.CharField(read_only=True)
    pay_type = serializers.CharField(read_only=True)
    add_time = serializers.CharField(read_only=True)

    def generate_order_sn(self):
        # 生成订单号
        # 当前时间 + userid + 随机数
        random_ins = Random()
        order_sn = "{time_str}{userid}{ranstr}".format(time_str=time.strftime("%Y%m%d%H%M%S"),
                                                       userid=self.context["request"].user.id,
                                                       ranstr=random_ins.randint(10, 99))
        return order_sn

    def validate(self, attrs):
        # vaildate中添加order_sn， 然后在view中就可以进行save
        attrs['order_sn'] = self.generate_order_sn()
        return attrs

    class Meta:
        model = OrderInfo
        fields = '__all__'
