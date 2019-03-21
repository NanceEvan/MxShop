"""MxShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import xadmin
from django.urls import path, include
from django.views.static import serve
# drf自带token认证
from rest_framework.authtoken import views
# jwt token认证
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from MxShop.settings import MEDIA_ROOT

from goods.views import GoodsListViewSet, GoodsCategoryViewSet, BannerViewSet, HotSearchWordsViewSet, \
    IndexCategoryViewset

# 配置goods的url
from trade.views import ShopCartViewSet, OrderViewSet
from user_operation.views import VerifyCodeViewSet, UserFavViewSet, UserMessageViewSet, UserAddressViewSet
from users.views import UsersViewSet

router = DefaultRouter()
router.register('goods', GoodsListViewSet)
router.register('categorys', GoodsCategoryViewSet)
router.register('code', VerifyCodeViewSet)
router.register('users', UsersViewSet)
router.register('userfavs', UserFavViewSet)
router.register('messages', UserMessageViewSet)
router.register('address', UserAddressViewSet)
router.register('shopcarts', ShopCartViewSet)
router.register('orders', OrderViewSet)
router.register('banners', BannerViewSet)
router.register('hotsearchs', HotSearchWordsViewSet)
router.register('indexgoods', IndexCategoryViewset)

# router.register('priceRange', PriceRangeView Set)


urlpatterns = [
    path('xadmin/', xadmin.site.urls),
    path('ueditor/', include('DjangoUeditor.urls')),
    path('api-auth/', include('rest_framework.urls')),
    # 文件
    path('media/<path:path>', serve, {'document_root': MEDIA_ROOT}),

    # 商品列表页
    # path('goods/', GoodsListView.as_view(), name='goods-list'),
    # path('goods/', goods_list, name='goods-list'),
    path('', include(router.urls)),

    path('docs/', include_docs_urls(title="MX生鲜")),

    # drf 自带的token
    # path('api-token-auth/', views.obtain_auth_token),
    path('api-token-auth/', verify_jwt_token),
    # jwt的token认证
    path('login/', obtain_jwt_token),
]
