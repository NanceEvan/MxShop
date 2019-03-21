# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from goods.filters import GoodsFilter
from goods.models import Goods, GoodsCategory, Banner, HotSearchWords
from goods.serializers import GoodsSerializer, GoodsCategorySerializer, BannerSerializer, HotSearchWordsSerializer, \
    IndexCategorySerializer


# class GoodsListView(APIView):
#     """
#         list all goods
#     """
#     def get(self, request, format=None):
#         goods = Goods.objects.all()[:10]
#         # 如果goods是一个列表， 必须加上参数many=True
#         goods_serializer = GoodsSerializer(goods, many=True)
#         return Response(goods_serializer.data)
#
#     # 商品的添加通过xadmin后台添加
#     # def post(self, request):
#     #     serializer = GoodsSerializer(data=request.data)
#     #     if serializer.is_valid():
#     #         serializer.save()
#     #         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# class GoodsListView(mixins.ListModelMixin, generics.GenericAPIView):
#     """
#         商品列表页
#     """
#     queryset = Goods.objects.all()
#     serializer_class = GoodsSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

# 设置分页
class GoodsPagination(PageNumberPagination):
    # 默认每页显示的个数
    page_size = 12
    # 可以动态改变每页显示的个数
    page_size_query_param = 'page_size'
    # 页码参数
    page_query_param = 'page'
    # 最多能显示的页数
    max_page_size = 100

#
# class GoodsListView(generics.ListAPIView):
#     """
#         商品列表页
#     """
#     queryset = Goods.objects.all()
#     serializer_class = GoodsSerializer
#     pagination_class = GoodsPagination
#
#     permission_classes = (AllowAny, )AllowAny


class HotSearchWordsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    搜索热词
    list:
        获取热搜词
    """
    queryset = HotSearchWords.objects.all().order_by('-index')
    serializer_class = HotSearchWordsSerializer


class BannerViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    首页轮播图
    list：
        获取首页轮播图
    """
    queryset = Banner.objects.all().order_by('index')
    serializer_class = BannerSerializer


class GoodsListViewSet(CacheResponseMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        获取商品列表页
    retrieve:
        获取商品详细信息
    """
    queryset = Goods.objects.all().order_by('id')
    serializer_class = GoodsSerializer

    pagination_class = GoodsPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)

    throttle_classes = (UserRateThrottle, AnonRateThrottle)

    permission_classes = (AllowAny, )
    # filter_fields = ('name', 'shop_price')
    # 字段过滤
    filterset_class = GoodsFilter
    # 全局搜索
    search_fields = ('name', 'goods_brief', 'goods_desc')
    # 排序
    ordering_fields = ('sold_num', 'shop_price')

    def retrieve(self, request, *args, **kwargs):
        """
            点击详情， 商品点击数+1
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        instance = self.get_object()
        instance.click_num += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class GoodsCategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    """
        list:
            商品分类列表数据
        retrieve:
            商品分类详细信息
    """
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = GoodsCategorySerializer
    permission_classes = (AllowAny, )


class IndexCategoryViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    首页商品分类数据
    """
    # 获取is_tab=True（导航栏）里面的分类下的商品数据
    queryset = GoodsCategory.objects.filter(is_tab=True)
    serializer_class = IndexCategorySerializer


# class PriceRangeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     """
#         list:
#             价格区间列表数据
#     """
#
#     queryset = PriceRange.objects.all()
#     serializer_class = PriceRangeSerializer

