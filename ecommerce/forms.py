from django import forms
from .models import (
    Order, ProductReview, ShippingAddress
)


class OrderCreateForm(forms.ModelForm):
    """Form for creating a new order"""
    payment_method = forms.ChoiceField(
        choices=[
            ('cod', 'Cash on Delivery'),
            ('card', 'Credit/Debit Card'),
            ('upi', 'UPI'),
            ('wallet', 'Digital Wallet')
        ],
        widget=forms.RadioSelect,
        initial='cod'
    )
    
    special_dietary_needs = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )
    
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address', 'postal_code', 'city', 'state',
            'payment_method', 'special_dietary_needs'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class ProductReviewForm(forms.ModelForm):
    """Form for product reviews"""
    trimester_when_used = forms.ChoiceField(
        choices=[
            ('First', 'First Trimester'),
            ('Second', 'Second Trimester'),
            ('Third', 'Third Trimester')
        ],
        required=False
    )
    
    class Meta:
        model = ProductReview
        fields = ['rating', 'review_text', 'trimester_when_used']
        widgets = {
            'review_text': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.RadioSelect(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
        }


class CouponApplyForm(forms.Form):
    """Form for coupon code application"""
    code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter coupon code'
        })
    )


class ShippingAddressForm(forms.ModelForm):
    """Form for shipping addresses"""
    is_default = forms.BooleanField(
        label='Set as default address',
        required=False
    )
    
    class Meta:
        model = ShippingAddress
        fields = [
            'name', 'phone', 'address_line1', 'address_line2',
            'city', 'state', 'postal_code', 'is_default'
        ]
        widgets = {
            'address_line1': forms.TextInput(attrs={'placeholder': 'Street address, P.O. box, etc.'}),
            'address_line2': forms.TextInput(attrs={'placeholder': 'Apartment, suite, building, etc. (optional)'})
        }