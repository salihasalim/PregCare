# Generated by Django 5.1.7 on 2025-03-10 09:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0003_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CartModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('is_order_placed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('product_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce.product')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItemModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('price', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('product_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce.product')),
            ],
        ),
        migrations.CreateModel(
            name='OrderModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.TextField()),
                ('phone', models.CharField(max_length=20)),
                ('payment_method', models.CharField(choices=[('COD', 'COD'), ('ONLINE', 'ONLINE')], default='COD', max_length=15)),
                ('rzp_order_id', models.CharField(max_length=100, null=True)),
                ('is_paid', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReviewModels',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('review_text', models.TextField(blank=True, null=True)),
                ('images', models.ImageField(blank=True, null=True, upload_to='review_images/')),
                ('verified_purchase', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='ecommerce.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='cart',
            name='user',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='cart',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='product',
        ),
        migrations.DeleteModel(
            name='Coupon',
        ),
        migrations.RemoveField(
            model_name='nutritionplan',
            name='recommended_products',
        ),
        migrations.RemoveField(
            model_name='nutritionplan',
            name='related_diet_plan',
        ),
        migrations.RemoveField(
            model_name='order',
            name='user',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='order',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='product',
        ),
        migrations.AlterUniqueTogether(
            name='productreview',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='productreview',
            name='product',
        ),
        migrations.RemoveField(
            model_name='productreview',
            name='user',
        ),
        migrations.AlterUniqueTogether(
            name='producttrimesterbenefit',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='producttrimesterbenefit',
            name='product',
        ),
        migrations.RemoveField(
            model_name='shippingaddress',
            name='user',
        ),
        migrations.AlterUniqueTogether(
            name='wishlist',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='wishlist',
            name='product',
        ),
        migrations.RemoveField(
            model_name='wishlist',
            name='user',
        ),
        migrations.AddField(
            model_name='orderitemmodel',
            name='order_object',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orderitems', to='ecommerce.ordermodel'),
        ),
        migrations.DeleteModel(
            name='Cart',
        ),
        migrations.DeleteModel(
            name='CartItem',
        ),
        migrations.DeleteModel(
            name='NutritionPlan',
        ),
        migrations.DeleteModel(
            name='Order',
        ),
        migrations.DeleteModel(
            name='OrderItem',
        ),
        migrations.DeleteModel(
            name='ProductReview',
        ),
        migrations.DeleteModel(
            name='ProductTrimesterBenefit',
        ),
        migrations.DeleteModel(
            name='ShippingAddress',
        ),
        migrations.DeleteModel(
            name='WishList',
        ),
    ]
