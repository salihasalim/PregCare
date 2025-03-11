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
    path('product/<int:pk>/details/',views.ProductDetailView.as_view(),name='product_detail'),

    path('addtocart/<int:pk>/',views.AddToCartView.as_view(),name="add-to-cart"),
    path('cart/summary/',views.CartSummaryView.as_view(),name='cart-summary'),
    path('cart/<int:pk>/remove/',views.CartItemDeleteView.as_view(),name='cart-item-remove'),
    path('place/order/',views.PlaceOrderView.as_view(),name='place-order'),
    path('success/msg/',views.OrderSuccessMessage.as_view(),name='order-success'),
    path('order/summary/',views.OrderSummaryView.as_view(),name='order-summary'),
    path('payment/verify/',views.PaymentVerificationsView.as_view(), name='payment-verification'),



    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)