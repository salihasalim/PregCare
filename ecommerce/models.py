from django.db import models
from care.models import User
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
    


class CartModel(models.Model):

    product_object=models.ForeignKey(Product,on_delete=models.CASCADE)

    owner=models.ForeignKey(User,on_delete=models.CASCADE)

    quantity=models.PositiveIntegerField()

    is_order_placed=models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now_add=True)


    def item_total(self):

        return self.quantity*self.product_object.price


class OrderModel(models.Model):

    customer=models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")

    address=models.TextField(null=False, blank=False)

    phone=models.CharField(max_length=20, null=False, blank=False)
    
    PAYMENT_OPTIONS=(
        ("COD","COD"),
        ("ONLINE","ONLINE")
    )

    payment_method=models.CharField(max_length=15, choices=PAYMENT_OPTIONS, default="COD")

    rzp_order_id=models.CharField(max_length=100, null=True)

    is_paid=models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now_add=True)

    def order_total(self):

        total = 0

        order_items=self.orderitems.all()

        if order_items:

            total = sum([oi.item_total() for oi in order_items])

        return total    
    


class OrderItemModel(models.Model):

    order_object=models.ForeignKey(OrderModel,on_delete=models.CASCADE, related_name="orderitems")

    product_object=models.ForeignKey(Product, on_delete=models.CASCADE)
    
    quantity=models.PositiveIntegerField(default=1)
    
    price=models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now_add=True)

    def item_total(self):
        
        return self.price*self.quantity  


class ReviewModels(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")

    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 rating

    review_text = models.TextField(blank=True, null=True)

    images = models.ImageField(upload_to="review_images/", blank=True, null=True)

    verified_purchase = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating} stars)"        



