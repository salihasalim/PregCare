from django import forms
from .models import (
    OrderModel,ReviewModels
)


class OrderForm(forms.ModelForm):

    class Meta:

        model = OrderModel 

        fields = ["address","phone","payment_method"]

#review form

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewModels

        fields = ['rating', 'review_text', 'images']
        
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)], attrs={'class': 'form-control'}),
            'review_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'images': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }      