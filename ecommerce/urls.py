from django.contrib import admin
from django.urls import path
from ecommerce import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'ecommerce'

urlpatterns = [
    # Product URLs
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/category/<slug:category_slug>/', views.ProductListView.as_view(), name='product_list_by_category'),
    path('products/<int:id>/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:product_id>/review/', views.add_product_review, name='add_product_review'),
    path('recommended-products/', views.recommended_products, name='recommended_products'),
    path('<int:id>/<slug:slug>/', product_detail, name='product_detail'),
    # Cart URLs
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('cart/apply-coupon/', views.apply_coupon, name='apply_coupon'),
    
    # Order URLs
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/complete/', views.order_complete, name='order_complete'),
    
    # Wishlist URLs
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:item_id>/', views.wishlist_remove, name='wishlist_remove'),
    
    # Address management
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.address_add, name='address_add'),
    path('addresses/<int:address_id>/edit/', views.address_edit, name='address_edit'),
    path('addresses/<int:address_id>/delete/', views.address_delete, name='address_delete'),
    path('addresses/<int:address_id>/set-default/', views.set_default_address, name='set_default_address'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)