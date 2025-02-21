from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile,ExercisePlan,Reminder,BabyKickCount
from django.utils import timezone




class SignUpForm(UserCreationForm):

    class Meta:

        model=User

        fields=['username', 'email' , 'password1' , 'password2']

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control border border-5'
        self.fields['email'].widget.attrs['class'] = 'form-control border border-5'
        self.fields['password1'].widget.attrs['class'] = 'form-control border border-5'
        self.fields['password2'].widget.attrs['class'] = 'form-control border border-5'
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        
        # Hide "Password-based authentication" field if it exists
        if 'password_based_authentication' in self.fields:
            self.fields['password_based_authentication'].widget = forms.HiddenInput()
        

class SignInForm(forms.Form):

    username = forms.CharField(max_length=100,
                               widget=forms.TextInput(attrs={'class': 'form-control mb-3 border-2px', 'placeholder': 'Enter your username'}))
    password = forms.CharField(max_length=200,
                               widget=forms.PasswordInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Enter your password'}))


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['lmp','expected_due_date', 'current_trimester','phone']
        widgets = {
            'lmp':forms.DateInput(attrs={'type':'date'}),
            'expected_due_date': forms.DateInput(attrs={'type': 'date'}),
            'current_trimester': forms.Select(attrs={'class': 'form-control'}),
            "phone":forms.NumberInput(attrs={"class":"form-control","style":"width:350px;height:40px;margin-bottom:40px;"})

        }

    def _init_(self, *args, **kwargs):
        super(UserProfileForm, self)._init_(*args, **kwargs)
        self.fields['expected_due_date'].widget.attrs.update({'class': 'form-control'})

    def _init_(self, *args, **kwargs):
        super(UserProfileForm, self)._init_(*args, **kwargs)
        today = timezone.now().date()  # Get today's date
        self.fields['lmp'].widget.attrs['max'] = today  # Set max to today's date



class ExercisePlanForm(forms.ModelForm):
    class Meta:
        model = ExercisePlan
        fields = ['title', 'description', 'video_url', 'trimester']



class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ['title', 'description', 'reminder_type', 'reminder_date']
        widgets = {
            'reminder_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }





class BabyKickForm(forms.ModelForm):
    class Meta:
        model=BabyKickCount
        fields = ['kick_count', 'trimester']

    kick_count = forms.IntegerField(label='Number of Kicks')
    trimester = forms.ChoiceField(choices=[('First', 'First Trimester'), ('Second', 'Second Trimester'), ('Third', 'Third Trimester')], label='Trimester')

