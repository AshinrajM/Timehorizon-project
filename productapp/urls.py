from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.shop, name="shop"),
    path("shop-by-catgeory/<int:category_id>", views.shop_by_category, name="shop_by_category"),
    path("shop-by-brand/<int:brand_id>", views.shop_by_brand, name="shop_by_brand"),
    path("product-detail/<int:product_id>/", views.product_detail, name="product_detail"),
    path("product-search/", views.product_search, name="product_search"),
    path("product-filter-by-price/", views.filter_by_price, name="product_filter_by_price"),
    path("ascending-sort/",views.ascending_sort,name="ascending_sort"),
    path("descending-sort/",views.descending_sort,name="descending_sort")
]
