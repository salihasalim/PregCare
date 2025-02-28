from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from care.models import DietPlan


class NutrientCategory(models.Model):
    """Categories of nutrients especially important during pregnancy"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    """Product categories for pregnancy diet foods"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'product categories'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('ecommerce:product_list_by_category', args=[self.slug])


class Product(models.Model):
    """Product model specifically for pregnancy diet foods"""
    category = models.ForeignKey(ProductCategory, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    
    # Pregnancy-specific fields
    # Using your existing trimester choices
    TRIMESTER_CHOICES = [
        ('First', 'First Trimester'),
        ('Second', 'Second Trimester'),
        ('Third', 'Third Trimester'),
    ]
    recommended_trimesters = models.CharField(max_length=100, choices=[
        ('All', 'All Trimesters'),
        ('First', 'First Trimester'),
        ('Second', 'Second Trimester'),
        ('Third', 'Third Trimester'),
        ('First,Second', 'First & Second Trimesters'),
        ('Second,Third', 'Second & Third Trimesters'),
        ('First,Third', 'First & Third Trimesters'),
    ], default='All')
    
    key_nutrients = models.ManyToManyField(NutrientCategory, blank=True)
    
    # Health information
    calories = models.PositiveIntegerField(default=0)
    protein = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    carbohydrates = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fats = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fiber = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    iron = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    calcium = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    folate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    # Dietary flags
    is_organic = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    is_dairy_free = models.BooleanField(default=False)
    
    # Product details
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ('name',)
        indexes = [
                models.Index(fields=['id', 'slug'])
         ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:product_detail', args=[self.id, self.slug])
    
    def get_discount_percentage(self):
        if self.discount_price:
            return int(100 - (self.discount_price * 100) / self.price)
        return 0


class Cart(models.Model):
    """Shopping cart model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart {self.id}"
    
    def get_total_price(self):
        return sum(item.get_cost() for item in self.items.all())
    
    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Individual items in a cart"""
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
    
    def get_cost(self):
        if self.product.discount_price:
            return self.product.discount_price * self.quantity
        return self.product.price * self.quantity


class Order(models.Model):
    """Order model for completed purchases"""
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, choices=[
        ('cod', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
        ('wallet', 'Digital Wallet')
    ], default='cod')
    
    # Integrate with existing pregnancy info
    trimester = models.CharField(max_length=20, choices=[
        ('First', 'First Trimester'),
        ('Second', 'Second Trimester'),
        ('Third', 'Third Trimester')
    ], blank=True, null=True)
    special_dietary_needs = models.TextField(blank=True)
    
    class Meta:
        ordering = ('-created_date',)
    
    def __str__(self):
        return f'Order {self.id}'
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all()) + self.shipping_cost
    
    def get_items_count(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """Individual items within an order"""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f'{self.id}'
    
    def get_cost(self):
        return self.price * self.quantity


class ProductReview(models.Model):
    """Customer reviews for products"""
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    review_text = models.TextField()
    trimester_when_used = models.CharField(max_length=20, choices=[
        ('First', 'First Trimester'),
        ('Second', 'Second Trimester'),
        ('Third', 'Third Trimester')
    ], blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('product', 'user')
        ordering = ('-created_date',)
    
    def __str__(self):
        return f'{self.user.username} rated {self.product.name} {self.rating}/5'


class WishList(models.Model):
    """User wishlist for products"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')
    
    def __str__(self):
        return f"{self.user.username}'s wishlist item: {self.product.name}"


class Coupon(models.Model):
    """Discount coupons"""
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(help_text="Percentage discount")
    active = models.BooleanField(default=True)
    
    # Trimester-specific coupons
    applicable_trimester = models.CharField(max_length=20, choices=[
        ('All', 'All Trimesters'),
        ('First', 'First Trimester'),
        ('Second', 'Second Trimester'),
        ('Third', 'Third Trimester')
    ], default='All')
    
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return self.code


class NutritionPlan(models.Model):
    """Nutrition plans - links diet plans to product recommendations"""
    name = models.CharField(max_length=100)
    trimester = models.CharField(max_length=20, choices=[
        ('First', 'First Trimester'),
        ('Second', 'Second Trimester'),
        ('Third', 'Third Trimester')
    ])
    description = models.TextField()
    
    # Link to existing diet plans
    related_diet_plan = models.ForeignKey(DietPlan, on_delete=models.SET_NULL, null=True, blank=True, 
                                          related_name='product_recommendations')
    
    # Products recommended in this plan
    recommended_products = models.ManyToManyField(Product, related_name='nutrition_plans')
    
    class Meta:
        ordering = ('trimester', 'name')
    
    def __str__(self):
        return f"{self.name} - {self.trimester}"


class ShippingAddress(models.Model):
    """User's shipping addresses"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping_addresses')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=250)
    address_line2 = models.CharField(max_length=250, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s address: {self.name}, {self.city}"


class ProductTrimesterBenefit(models.Model):
    """Specific benefits of products for each trimester"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='trimester_benefits')
    trimester = models.CharField(max_length=20, choices=[
        ('First', 'First Trimester'),
        ('Second', 'Second Trimester'),
        ('Third', 'Third Trimester')
    ])
    benefit_description = models.TextField()
    
    class Meta:
        unique_together = ('product', 'trimester')
    
    def __str__(self):
        return f"{self.product.name} benefits for {self.trimester} Trimester"