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

from .models import (
    Product, ProductCategory, NutrientCategory, Cart, CartItem,
    Order, OrderItem, ProductReview, WishList, Coupon, NutritionPlan,
    ShippingAddress, ProductTrimesterBenefit
)
from .forms import (
    OrderCreateForm, ProductReviewForm, CouponApplyForm, 
    ShippingAddressForm
)


# Product Views
class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(available=True, is_active=True)
        
        # Filter by category if specified
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(ProductCategory, slug=category_slug)
            queryset = queryset.filter(category=category)
        
        # Filter by trimester if specified
        trimester = self.request.GET.get('trimester')
        if trimester:
            queryset = queryset.filter(
                Q(recommended_trimesters=trimester) | 
                Q(recommended_trimesters='All') |
                Q(recommended_trimesters__contains=trimester)
            )
        
        # Filter by dietary requirements
        if self.request.GET.get('organic'):
            queryset = queryset.filter(is_organic=True)
        if self.request.GET.get('gluten_free'):
            queryset = queryset.filter(is_gluten_free=True)
        if self.request.GET.get('dairy_free'):
            queryset = queryset.filter(is_dairy_free=True)
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Sort products
        sort_by = self.request.GET.get('sort_by', 'name')
        if sort_by == 'price_low':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_date')
        else:
            queryset = queryset.order_by('name')
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProductCategory.objects.all()
        
        # Add trimester choices for filtering
        context['trimester_choices'] = [
            ('First', 'First Trimester'),
            ('Second', 'Second Trimester'),
            ('Third', 'Third Trimester'),
        ]
        
        # Get current user's trimester if logged in
        if self.request.user.is_authenticated:
            try:
                user_profile = self.request.user.userprofile
                context['user_trimester'] = user_profile.current_trimester
            except:
                context['user_trimester'] = None
        
        # Category for breadcrumbs
        if 'category_slug' in self.kwargs:
            context['current_category'] = get_object_or_404(
                ProductCategory, 
                slug=self.kwargs['category_slug']
            )
        
        # Keep track of query parameters for pagination links
        context['query_params'] = self.request.GET.copy()
        if 'page' in context['query_params']:
            del context['query_params']['page']
        
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Related products (same category)
        context['related_products'] = Product.objects.filter(
            category=product.category, 
            available=True, 
            is_active=True
        ).exclude(id=product.id)[:4]
        
        # Get product reviews
        context['reviews'] = product.reviews.all().order_by('-created_date')
        context['avg_rating'] = product.reviews.aggregate(
            avg_rating=Avg('rating')
        )['avg_rating']
        
        # Add review form
        context['review_form'] = ProductReviewForm()
        
        # Check if user has already reviewed this product
        if self.request.user.is_authenticated:
            context['user_has_reviewed'] = product.reviews.filter(
                user=self.request.user
            ).exists()
            
            # Check if product is in user's wishlist
            context['in_wishlist'] = WishList.objects.filter(
                user=self.request.user, 
                product=product
            ).exists()
            
            # Get user's trimester for tailored information
            try:
                user_trimester = self.request.user.userprofile.current_trimester
                context['user_trimester'] = user_trimester
                
                # Get trimester-specific benefits
                try:
                    trimester_benefit = product.trimester_benefits.get(
                        trimester=user_trimester
                    )
                    context['trimester_benefit'] = trimester_benefit
                except ProductTrimesterBenefit.DoesNotExist:
                    pass
            except:
                pass
        
        return context


@login_required
def add_product_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            # Check if user has already reviewed this product
            existing_review = ProductReview.objects.filter(
                user=request.user, 
                product=product
            ).first()
            
            if existing_review:
                # Update existing review
                existing_review.rating = form.cleaned_data['rating']
                existing_review.review_text = form.cleaned_data['review_text']
                existing_review.trimester_when_used = form.cleaned_data['trimester_when_used']
                existing_review.save()
                messages.success(request, 'Your review has been updated.')
            else:
                # Create new review
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, 'Thank you for your review!')
                
            return redirect('product_detail', id=product.id, slug=product.slug)
    
    return redirect('product_detail', id=product.id, slug=product.slug)


# Cart Views
@login_required


def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    # Handle both authenticated and anonymous users
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # Get cart from session or create a new one for anonymous users
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                cart = Cart.objects.create(user=None)
                request.session['cart_id'] = cart.id
        else:
            cart = Cart.objects.create(user=None)
            request.session['cart_id'] = cart.id
    
    # Check if product is already in cart
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.quantity += quantity
        cart_item.save()
    except CartItem.DoesNotExist:
        CartItem.objects.create(cart=cart, product=product, quantity=quantity)
    
    messages.success(request, f'{product.name} added to your cart.')
    
    # Check if user wants to continue shopping or go to cart
    if request.POST.get('redirect_to_cart'):
        return redirect('ecommerce:cart_detail')  # Make sure this matches your URL name
    
    # Make sure these parameters match your URL pattern
    return redirect(reverse('ecommerce:product_detail', kwargs={'id': product.id, 'slug': product.slug}))

@login_required
def cart_remove(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from your cart.')
    return redirect('cart_detail')


@login_required
def cart_update(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    
    return redirect('cart_detail')


@login_required
def cart_detail(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        cart = None
        cart_items = []
    
    coupon_form = CouponApplyForm()
    
    # Check for active coupon
    coupon_id = request.session.get('coupon_id')
    coupon = None
    discount = Decimal('0.00')
    
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id, active=True)
            # Check if coupon is valid for user's trimester
            if cart and cart_items:
                user_trimester = request.user.userprofile.current_trimester
                if coupon.applicable_trimester in ['All', user_trimester]:
                    # Calculate discount
                    subtotal = sum(item.get_cost() for item in cart_items)
                    if subtotal >= coupon.min_purchase_amount:
                        discount = subtotal * (coupon.discount / Decimal('100'))
                        if coupon.max_discount_amount:
                            discount = min(discount, coupon.max_discount_amount)
        except Coupon.DoesNotExist:
            # Invalid coupon, remove from session
            request.session.pop('coupon_id', None)
    
    return render(request, 'cart/cart_detail.html', {
        'cart': cart,
        'cart_items': cart_items,
        'coupon_form': coupon_form,
        'coupon': coupon,
        'discount': discount
    })


@login_required
def apply_coupon(request):
    if request.method == 'POST':
        form = CouponApplyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            now = timezone.now()
            
            try:
                coupon = Coupon.objects.get(
                    code__iexact=code,
                    valid_from__lte=now,
                    valid_to__gte=now,
                    active=True
                )
                
                # Check if coupon is valid for user's trimester
                user_trimester = request.user.userprofile.current_trimester
                if coupon.applicable_trimester not in ['All', user_trimester]:
                    messages.error(
                        request, 
                        f'This coupon is only valid for {coupon.applicable_trimester} Trimester.'
                    )
                    return redirect('cart_detail')
                
                # Check minimum purchase amount
                cart = Cart.objects.get(user=request.user)
                cart_total = sum(item.get_cost() for item in cart.items.all())
                
                if cart_total < coupon.min_purchase_amount:
                    messages.error(
                        request, 
                        f'This coupon requires a minimum purchase of ${coupon.min_purchase_amount}.'
                    )
                    return redirect('cart_detail')
                
                # Store coupon in session
                request.session['coupon_id'] = coupon.id
                messages.success(
                    request, 
                    f'Coupon "{code}" applied with {coupon.discount}% discount!'
                )
            except Coupon.DoesNotExist:
                request.session.pop('coupon_id', None)
                messages.error(request, 'This coupon is invalid or expired.')
        
    return redirect('cart_detail')


# Order Views
@login_required
def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        
        if not cart_items:
            messages.warning(request, 'Your cart is empty. Add some products first.')
            return redirect('product_list')
            
    except Cart.DoesNotExist:
        messages.warning(request, 'Your cart is empty. Add some products first.')
        return redirect('product_list')
    
    # Get user's saved addresses
    addresses = ShippingAddress.objects.filter(user=request.user)
    
    # Calculate totals
    subtotal = sum(item.get_cost() for item in cart_items)
    
    # Apply coupon if available
    coupon_id = request.session.get('coupon_id')
    coupon = None
    discount = Decimal('0.00')
    
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id, active=True)
            # Check if coupon is valid for current user's trimester
            user_trimester = request.user.userprofile.current_trimester
            if coupon.applicable_trimester in ['All', user_trimester]:
                discount = subtotal * (coupon.discount / Decimal('100'))
                if coupon.max_discount_amount:
                    discount = min(discount, coupon.max_discount_amount)
        except Coupon.DoesNotExist:
            request.session.pop('coupon_id', None)
    
    # Fixed shipping cost (could be made variable based on location/order size)
    shipping_cost = Decimal('5.00')
    total = subtotal - discount + shipping_cost
    
    # Pre-fill form with user data
    initial_data = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
    }
    
    # Try to get phone from user profile
    try:
        initial_data['phone'] = request.user.userprofile.phone
    except:
        pass
    
    # Try to get default address
    default_address = addresses.filter(is_default=True).first()
    if default_address:
        initial_data.update({
            'address': default_address.address_line1,
            'city': default_address.city,
            'state': default_address.state,
            'postal_code': default_address.postal_code,
        })
    
    # Create form with initial data
    form = OrderCreateForm(initial=initial_data)
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Create the order
            order = form.save(commit=False)
            order.user = request.user
            
            # Add pregnancy-specific info
            try:
                order.trimester = request.user.userprofile.current_trimester
            except:
                pass
            
            # Add shipping and coupon info
            order.shipping_cost = shipping_cost
            if coupon:
                order.coupon = coupon
                order.discount = discount
            
            order.save()
            
            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.discount_price or item.product.price,
                    quantity=item.quantity
                )
            
            # Clear cart and coupon
            cart_items.delete()
            request.session.pop('coupon_id', None)
            
            # Go to payment (or complete order if COD)
            if order.payment_method == 'cod':
                messages.success(
                    request, 
                    'Your order has been placed successfully. Thank you for shopping with us!'
                )
                return redirect('order_complete', order_id=order.id)
            else:
                # Here you would redirect to payment gateway
                # For now, we'll just mark as paid and complete the order
                order.paid = True
                order.save()
                messages.success(
                    request, 
                    'Your order has been placed and payment received. Thank you for shopping with us!'
                )
                return redirect('order_complete', order_id=order.id)
    
    return render(request, 'orders/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'addresses': addresses,
        'subtotal': subtotal,
        'discount': discount,
        'shipping_cost': shipping_cost,
        'total': total,
        'coupon': coupon
    })


@login_required
def order_complete(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Calculate nutrition totals for this order
    nutrition_totals = {
        'calories': 0,
        'protein': 0,
        'carbohydrates': 0,
        'fats': 0,
        'fiber': 0,
        'iron': 0,
        'calcium': 0,
        'folate': 0,
    }
    
    for item in order.items.all():
        for nutrient in nutrition_totals:
            if hasattr(item.product, nutrient):
                value = getattr(item.product, nutrient)
                if value:
                    nutrition_totals[nutrient] += value * item.quantity
    
    return render(request, 'orders/order_complete.html', {
        'order': order,
        'nutrition_totals': nutrition_totals
    })


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_date')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


# Wishlist Views
@login_required
def wishlist_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if already in wishlist
    wishlist_item, created = WishList.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        messages.success(request, f'{product.name} added to your wishlist.')
    else:
        messages.info(request, f'{product.name} is already in your wishlist.')
    
    # Redirect based on request source
    next_url = request.GET.get('next', '')
    if next_url:
        return redirect(next_url)
    return redirect('ecommetrce:product_detail', id=product.id, slug=product.slug)


@login_required
def wishlist_remove(request, item_id):
    wishlist_item = get_object_or_404(WishList, id=item_id, user=request.user)
    product_name = wishlist_item.product.name
    wishlist_item.delete()
    messages.success(request, f'{product_name} removed from your wishlist.')
    return redirect('wishlist')


@login_required
def wishlist_view(request):
    wishlist_items = WishList.objects.filter(user=request.user).order_by('-added_date')
    return render(request, 'wishlist/wishlist.html', {'wishlist_items': wishlist_items})


# Recommendation Views
@login_required
def recommended_products(request):
    user_trimester = None
    
    try:
        user_profile = request.user.userprofile
        user_trimester = user_profile.current_trimester
    except:
        messages.warning(
            request, 
            'Please update your pregnancy profile to get personalized recommendations.'
        )
        # Redirect to profile update page or show generic recommendations
        return redirect('product_list')
    
    # Get products recommended for user's trimester
    recommendations = Product.objects.filter(
        Q(recommended_trimesters=user_trimester) | 
        Q(recommended_trimesters='All') |
        Q(recommended_trimesters__contains=user_trimester),
        available=True, 
        is_active=True
    )
    
    # Get nutrition plans for this trimester
    nutrition_plans = NutritionPlan.objects.filter(trimester=user_trimester)
    
    # Find if user has a diet plan
    user_diet_plans = []
    try:
        user_diet_plans = user_profile.user.dietplan_set.filter(trimester=user_trimester)
    except:
        pass
    
    return render(request, 'products/recommended_products.html', {
        'user_trimester': user_trimester,
        'recommendations': recommendations,
        'nutrition_plans': nutrition_plans,
        'user_diet_plans': user_diet_plans
    })


# Shipping Address Views
@login_required
def address_list(request):
    addresses = ShippingAddress.objects.filter(user=request.user)
    return render(request, 'accounts/address_list.html', {'addresses': addresses})


@login_required
def address_add(request):
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            
            # If this is set as default, unset other defaults
            if address.is_default:
                ShippingAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
                
            address.save()
            messages.success(request, 'Shipping address added successfully.')
            return redirect('address_list')
    else:
        form = ShippingAddressForm()
    
    return render(request, 'accounts/address_form.html', {'form': form})


@login_required
def address_edit(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=address)
        if form.is_valid():
            # If this is set as default, unset other defaults
            if form.cleaned_data['is_default']:
                ShippingAddress.objects.filter(
                    user=request.user, 
                    is_default=True
                ).exclude(id=address.id).update(is_default=False)
                
            form.save()
            messages.success(request, 'Shipping address updated successfully.')
            return redirect('address_list')
    else:
        form = ShippingAddressForm(instance=address)
    
    return render(request, 'accounts/address_form.html', {'form': form, 'address': address})


@login_required
def address_delete(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Shipping address deleted successfully.')
        return redirect('address_list')
    
    return render(request, 'accounts/address_confirm_delete.html', {'address': address})


@login_required
def set_default_address(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    
    # Unset any existing default
    ShippingAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
    
    # Set new default
    address.is_default = True
    address.save()
    
    messages.success(request, f'{address.name}, {address.city} set as your default address.')
    return redirect('address_list')