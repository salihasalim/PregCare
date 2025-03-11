from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.db.models import Avg, Q
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from django.views.generic import View
from ecommerce.forms import ReviewForm
import razorpay
from .models import (
    Product, ProductCategory, NutrientCategory, CartModel,OrderModel,OrderItemModel
)
from .forms import (
    OrderForm,ReviewForm
)

RZP_KEY_ID='rzp_test_Sjy6Si9Hn24pDd'
RZP_KEY_SECRET='3nGtAZUZpwQz9DrxG4Q3WRYk'


# Product Views
class ProductListView(View):
    
    template_name = 'product_list.html'

    def get(self, request, *args, **kwargs):

        category = kwargs.get('category')  

        search_text = request.GET.get('search')

        products = Product.objects.all()


        print("========",search_text) 

        if search_text:

            products = products.filter(Q(name__icontains=search_text))  

            
       


        # if category:

        #     # print("==========", category)  

        #     category_obj = get_object_or_404(Category,name = category)

        #     products = products.filter(category=category_obj)

         

        return render(request, self.template_name, {'products': products})



class ProductDetailView(View):
    template_name = 'product_detail.html' 

    def get(self, request, *args, **kwargs):

        id = kwargs.get('pk')

        
        product = get_object_or_404(Product, id=id)

        # product_review = ReviewModels.objects.filter(product=product)

        return render(request, self.template_name, {'product': product})

    
class AddToCartView(View):

    def post(self, request, *args, **kwargs):

        if not request.user.is_authenticated:

            messages.error(request, "You must be logged in to add items to the cart.")

            return redirect('login') 

        product_id = kwargs.get('pk')

        product_instance = get_object_or_404(Product, id=product_id)       

        try:
            qty = request.POST.get('quantity') 
        except ValueError:
            messages.error(request, "Invalid quantity selected.")

            return redirect('product_detail', pk=product_id)

    
        CartModel.objects.create(
            product_object=product_instance,
            quantity=qty,
            owner=request.user
        )

        messages.success(request, "Product added to cart successfully!")

        return redirect('ecommerce:product_list')

class CartSummaryView(View):

    template_name  ='cart_summary.html'

    def get(self,request,*args,**kwargs):

        qs = CartModel.objects.filter(owner=request.user,is_order_placed = False)

        basket_total  = sum([c.item_total() for c in qs])

        return render(request,self.template_name,{'data':qs,'basket_total': basket_total}) 

    
class CartItemDeleteView(View):


    def get(self,request,*args,**kwargs):

        id = kwargs.get('pk')

        qs = CartModel.objects.get(id=id).delete()

        return redirect('ecommerce:cart-summary')  
    
class PlaceOrderView(View):

    template_name = 'place_order.html'

    form_class = OrderForm

    def get(self,request,*args,**kwargs):

        form_instance = self.form_class()

        qs = CartModel.objects.filter(owner=request.user,is_order_placed=False)

        basket_total = sum([c.item_total() for c in qs])

        return render(request,self.template_name,{'form':form_instance,'cartitems':qs,'total':basket_total})
    
    def post(self,request,*args,**kwargs):

        form_instance = self.form_class(request.POST)

        if form_instance.is_valid():

            form_instance.instance.customer = request.user   #here instance refer to the model given in model form

            order_object = form_instance.save()

            cart_items = CartModel.objects.filter(owner=request.user,is_order_placed = False)

            for ci in cart_items:

                OrderItemModel.objects.create(

                    order_object = order_object,
                    product_object = ci.product_object,
                    quantity = ci.quantity,
                    price = ci.product_object.price

                )

                ci.is_order_placed=True
                
                ci.save()


            payment_method = request.POST.get("payment_method") #ONLINE,COD

            if payment_method == 'ONLINE':

                client = razorpay.Client(auth=(RZP_KEY_ID,RZP_KEY_SECRET))

                data = { "amount": order_object.order_total()*100, "currency": "INR", "receipt": "order_rcptid_11" }

                payment = client.order.create(data=data)

                print("===============",payment)

                rzp_id = payment.get('id')

                order_object.rzp_order_id=rzp_id

                order_object.save()
                print(order_object.rzp_order_id)
                context = {
                    'key_id':RZP_KEY_ID,
                    'amount':order_object.order_total()*100,
                    'order_id':order_object.rzp_order_id

                }

                return render(request,'payment.html',context)

            return redirect('ecommerce:order-success')  
        
        
  
import json


class PaymentVerificationsView(View):

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))

        try:
            body = json.loads(request.body)
            rzp_order_id = body.get('razorpay_order_id')
            rzp_payment_id = body.get('razorpay_payment_id')
            rzp_signature = body.get('razorpay_signature')

            print("Received Razorpay Response:", body)

            # Verify the payment signature
            client.utility.verify_payment_signature({
                'razorpay_order_id': rzp_order_id,
                'razorpay_payment_id': rzp_payment_id,
                'razorpay_signature': rzp_signature
            })

            # Update order status
            OrderModel.objects.filter(rzp_order_id=rzp_order_id).update(is_paid=True)

            # Send JSON response with redirect URL
            return JsonResponse({"status": "success", "redirect_url": reverse('ecommerce:order-success')})

        except Exception as e:
            print('Payment Failed:', str(e))
            return JsonResponse({"status": "error", "message": "Payment verification failed"})


       

class OrderSuccessMessage(View):

    template_name ='order_success_msg.html'   

    def get(self,request,*args,**kwargs):


        return render(request,self.template_name) 

class OrderSummaryView(View):

    template_name = "order_summary.html"

    def get(self,request,*args,**kwargs):

        qs = OrderModel.objects.filter(customer = request.user).order_by("-created_at")

        return render(request,self.template_name,{'orders':qs})  


# class AddWishlistView(View):
#     def post(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             messages.error(request, "You must be logged in to add items to the wishlist.")
#             return JsonResponse({"error": "Authentication required"}, status=401)

#         product_id = kwargs.get('pk')
#         product_instance = get_object_or_404(Product, id=product_id)
        
#         wishlist, created = WishList.objects.get_or_create(user=request.user)

#         if product_instance in wishlist.product.all():
#             wishlist.product.remove(product_instance)
#             wishlist.refresh_from_db()
#             return JsonResponse({"removed": True})  
#         else:
#             wishlist.product.add(product_instance)
#             wishlist.refresh_from_db()
#             return JsonResponse({"added": True})  


# class WishlistView(View):
#     template_name = 'wishlist.html'

#     def get(self,request,*args,**kwargs):
    
#         wishlist, created = WishList.objects.get_or_create(user=request.user)
        
#         products = wishlist.product.all()  # Get all wishlist items

#         return render(request,self.template_name, {"wishlist_products": products})
    



#     def post(self, request, *args, **kwargs):
#         product_id = kwargs.get("pk")
#         product = get_object_or_404(Product, id=product_id)

#         # Remove the product from the wishlist
#         wishlist_item = WishList.objects.filter(user=request.user, product=product)
#         if wishlist_item.exists():
#             wishlist_item.delete()

#             # Get updated wishlist count
#             wishlist_count = WishList.objects.filter(user=request.user).count()
#             return JsonResponse({"removed": True, "wishlist_count": wishlist_count})

#         return JsonResponse({"removed": False, "wishlist_count": WishList.objects.filter(user=request.user).count()})
    

# class AddReviewView(View):

#     template_name = 'add_review.html'

#     form_class =  ReviewForm

#     def get(self,request,*args,**kwargs):

#         id = kwargs.get('pk')

#         qs = Product.objects.get(id=id)

#         form_instance = self.form_class() 

#         return render(request,self.template_name,{'form':form_instance,'product':qs}) 

#     def post(self,request,*args,**kwargs):

#         id = kwargs.get('pk') 

#         product = Product.objects.get(id=id)

#         form_instance = self.form_class(request.POST)

#         if form_instance.is_valid():

#             review = form_instance.save(commit=False)

#             review.user = request.user

#             review.product = product

#             review.verified_purchase = True  
            
#             review.save()

#             messages.success(request, "Your review has been submitted!")

#             return redirect('product-details', pk=product.id)
        
#         return render(request,self.template_name,{'form':form_instance})






