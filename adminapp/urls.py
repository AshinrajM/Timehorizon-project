from django.urls import path
from . import views

urlpatterns = [
    path("", views.admin_login, name="admin_login"),
    path("admin_logout/", views.admin_logout, name="admin_logout"),
    path("dashboard/", views.admin_dashboard, name="dashboard"),
    path("product/", views.admin_product, name="admin_product"),
    path(
        "product-active/<int:product_id>", views.product_active, name="product_active"
    ),
    path(
        "category-active/<int:category_id>",
        views.category_active,
        name="category_active",
    ),
    path(
        "sub-category-active/<int:sub_id>",
        views.sub_category_active,
        name="sub_category_active",
    ),
    path("add-product/", views.admin_add_product, name="admin_add_product"),
    path(
        "edit-product/<int:product_id>/",
        views.admin_edit_product,
        name="admin_edit_product",
    ),
    path(
        "update-product/<int:product_id>",
        views.admin_update_product,
        name="admin_update_product",
    ),
    path("category/", views.admin_category, name="admin_category"),
    path(
        "edit-category/<int:category_id>/",
        views.admin_edit_category,
        name="admin_edit_category",
    ),
    path(
        "update-category/<int:category_id>/",
        views.admin_update_category,
        name="admin_update_category",
    ),
    path("sub-category/", views.admin_sub_category, name="admin_sub_category"),
    path(
        "edit-sub-category/<int:sub_id>",
        views.admin_edit_sub_category,
        name="admin_edit_sub_category",
    ),
    path(
        "update-sub-category/<int:sub_id>",
        views.admin_update_sub_category,
        name="admin_update_sub_category",
    ),
    path("order/", views.admin_order, name="admin_order"),
    path(
        "order-details/<int:order_id>",
        views.admin_order_detail,
        name="admin_order_detail",
    ),
    path("users/", views.admin_user, name="admin_user"),
    path("users-active/<int:user_id>", views.user_active, name="user_active"),
    path("admin-coupon/", views.admin_coupon, name="admin_coupon"),
    path("admin-add-coupon/", views.admin_add_coupon, name="admin_add_coupon"),
    path(
        "admin-update-coupon/<int:coupon_id>/",
        views.admin_update_coupon,
        name="admin_update_coupon",
    ),
    path("admin-brand/", views.admin_brand, name="admin_brand"),
    path("admin-add-brand/", views.admin_add_brand, name="admin_add_brand"),
    path(
        "admin-update-brand/<int:brand_id>/",
        views.admin_update_brand,
        name="admin_update_brand",
    ),
    path("admin-banner/", views.admin_banner, name="admin_banner"),
    path(
        "admin-update-banner/<int:banner_id>/",
        views.admin_update_banner,
        name="admin_update_banner",
    ),
    path(
        "request-approve/<int:order_id>/",
        views.admin_request_approve,
        name="request_approve",
    ),
    path(
        "request-rejected/<int:order_id>/",
        views.admin_request_rejected,
        name="request_rejected",
    ),
    path('pdf-report/',views.pdf_report,name="pdf_report"),
]
