from django.shortcuts import render, redirect,get_object_or_404

from django.http import FileResponse, Http404

from django.views.generic import View,ListView

from django.db.models import Q

from django.contrib.auth.models import User

from care.models import UserProfile,ExercisePlan,Book,Reminder,PregnancyTip,BabyKickCount,DietPlan

from .forms import UserProfileForm,SignInForm,SignUpForm,ReminderForm,BabyKickForm

from django.contrib import messages

from django.contrib.auth import authenticate,login,logout

from django.contrib.auth.decorators import login_required

from care.decorators import signin_required

from django.utils.decorators import method_decorator


from django.views.decorators.cache import never_cache

from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.mail import send_mail

from django.utils import timezone

from datetime import datetime

from django.utils.timezone import localtime

from datetime import date

from django.http import HttpResponse






# Create your views here.
class IndexPageView(View):

    template_name='indexpage.html'

    def get(self,request,*args,**kwargs):

     return render(request,self.template_name)







class frontPageView(View):

    template_name='frontpage.html'

    def get(self,request,*args,**kwargs):

     return render(request,self.template_name)
     
from django.shortcuts import render
from django.views import View
from django.contrib.auth.models import User
from .models import UserProfile
import datetime



decs=[signin_required,never_cache]
@method_decorator(decs,name="dispatch")
class HomePageView(View):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        try:
            # Get the user's profile (assuming UserProfile is connected to User)
            user_profile = request.user.profile
            lmp = user_profile.lmp  # Last Menstrual Period

            # Calculate the pregnancy week (based on LMP)
            today = datetime.date.today()
            delta = today - lmp  # Get the difference between today and the LMP
            pregnancy_week = delta.days // 7  # Convert days to weeks

            # Ensure pregnancy_week is between 0 and 40 (as the pregnancy lasts around 40 weeks)
            if pregnancy_week > 40:
                pregnancy_week = 40

            # Decide which image to show based on the pregnancy week
            baby_image = f"images/week_{pregnancy_week}.png"

            # Render the homepage with the baby's size image
            return render(request, self.template_name, {
                'baby_image': baby_image,
                'pregnancy_week': pregnancy_week,
            })

        except AttributeError:
            # If the user does not have a profile or LMP, handle gracefully
            return render(request, self.template_name, {'error': 'Profile or LMP not set'})



class signUpView(View):

    template_name="Signup.html"

    form_class = SignUpForm

    def get(self,request,*args,**kwargs):

        form_instance = self.form_class()

        return render(request,self.template_name,{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        form_instance = self.form_class(request.POST)

        if form_instance.is_valid():

            form_instance.save()

            return redirect("signin")
        
        return render(request,self.template_name,{"form":form_instance})
    

class SignInView(View):

    template_name = "login.html"

    form_class = SignInForm

    def get(self,request,*args,**kwargs):

        form_instance = self.form_class()

        return render(request,self.template_name,{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        form_instance = self.form_class(request.POST)

        if form_instance.is_valid():

            uname = form_instance.cleaned_data.get("username")

            pwd = form_instance.cleaned_data.get("password")

            user_object = authenticate(request, username=uname,password=pwd)

            if user_object:

                login(request, user_object)

                messages.success(request,"login success")

                return redirect("home")
                
            else:

                messages.error(request,"invalid username or password")

        return render(request,self.template_name,{"form":form_instance})



decs=[signin_required,never_cache]
@method_decorator(decs,name="dispatch")
def user_profile(request):

    profile = request.user.userprofile

    if request.method == 'POST':

        form = UserProfileForm(request.POST, instance=profile)

        if form.is_valid():

            form.save()

            return redirect('home')

    else:

        form = UserProfileForm(instance=profile)

    return render(request, 'userprofile.html', {'form': form})




# EXERCISE PLAN


decs=[signin_required,never_cache]
@method_decorator(decs,name="dispatch")
class ExercisePlanView(LoginRequiredMixin, ListView):

    model = ExercisePlan

    template_name = 'exercise_plan.html'

    context_object_name = 'videos'

    def get_queryset(self):

        user_profile = self.request.user.userprofile 

        current_trimester = user_profile.current_trimester
        
        print(f"User's Current Trimester: {current_trimester}")


        return ExercisePlan.objects.filter(trimester=current_trimester)


        print(f"Number of Exercise Plans found: {exercise_plans.count()}")


# for book

decs=[signin_required,never_cache]
@method_decorator(decs,name="dispatch")
def explore_books(request):

    books = Book.objects.all()  

    return render(request, 'explore_books.html', {'books': books})



decs=[signin_required,never_cache]
@method_decorator(decs,name="dispatch")

def download_book(request,book_id):

    book = get_object_or_404(Book, id=book_id)

    try:

        response = FileResponse(book.book_file, as_attachment=True)

        return response

    except FileNotFoundError:

        raise Http404("Book file not found")


# for rfeminder

decs=[signin_required,never_cache]
@method_decorator(decs,name="dispatch")
class AddReminderView(View):

    template_name = 'add_reminder.html'
    
    def get(self,request,*args,**kwargs):

        form = ReminderForm()

        return render(request, self.template_name, {'form': form})
    
    def post(self,request,*args,**kwargs):

        form = ReminderForm(request.POST)

        if form.is_valid():

            reminder = form.save(commit=False)

            reminder.user = request.user 

            reminder.save()
            
            self.send_appointment_email(reminder)

            
            return redirect('reminder_list') 

        return render(request, self.template_name, {'form': form})
    
    def send_appointment_email(self, reminder):
        """Send an email to the user about their appointment."""
        subject = f"Reminder: Your {reminder.reminder_type} on {reminder.reminder_date}"
        
        message = f"""
       
                Dear {reminder.user.username},
                You have a {reminder.reminder_type} scheduled for {reminder.reminder_date}. Don't forget to attend!</p>
                For more information, you can visit our website:
                "https://yourwebsite.com"Click here to visit our website
                Best regards,PregCare Team
             """


        recipient_list = [reminder.user.email]  

        send_mail(subject, message, 'salishamnas215@gmail.com', {self.request.user.email})




decs=[signin_required,never_cache]
@method_decorator(decs,name="dispatch")
class ReminderListView(View):

    template_name = 'reminder_list.html'
    
    def get(self,request,*args,**kwargs):

        reminders = Reminder.objects.filter(user=request.user).order_by('reminder_date')

      
        return render(request, self.template_name, {'reminders': reminders})


decs=[signin_required,never_cache]
@method_decorator(decs,name="dispatch")
class MarkAsCompletedView(View):
    
    def get(self, request, reminder_id, *args, **kwargs):

        reminder = Reminder.objects.get(id=reminder_id)
        
        if reminder.user == request.user:

            reminder.is_completed = True

            reminder.save()
            
        return redirect('reminder_list')

# for pregnancy tips


decs=[signin_required,never_cache]
@method_decorator(decs,name="dispatch")
def get_current_week_of_pregnancy(lmp_date):

    if lmp_date:

        today = date.today()

        delta = today - lmp_date

        current_week = (delta.days // 7) + 1  

        return current_week
    return None

decs=[signin_required,never_cache]
@method_decorator(decs,name="dispatch")
class PregnancyTipsView(View):
    template_name = 'pregnancy_tips.html'
    
    def get(self, request, *args, **kwargs):
        # Get the user's profile using the 'mother' field
        user_profile = UserProfile.objects.get(mother=request.user)
        current_trimester = user_profile.current_trimester

        # Fetch tips based on the current trimester
        if current_trimester:

            tips = PregnancyTip.objects.filter(trimester=current_trimester)
            
        else:
            tips = PregnancyTip.objects.all()  # Default to all tips if no trimester is available

        # Pass the tips and current trimester information to the template
        return render(request, self.template_name, {
            'tips': tips,
            'current_trimester': current_trimester,
        })




# kick count'


# def check_kick_normality(kick_data):
#     """Check if the kick count is within the normal range for the trimester."""
#     kick_count = kick_data.kick_count  # Using 'kick_count' from your model
#     trimester = kick_data.trimester  # Using trimester from the model

#     # Trimester-specific kick count ranges
#     normal_kick_ranges = {
#         'First': (0, 10),  # First trimester kicks are less frequent
#         'Second': (10, 20),  # Second trimester may range higher
#         'Third': (20, 40),  # Third trimester kicks could range around this
#     }

#     min_kicks, max_kicks = normal_kick_ranges.get(trimester, (0, 0))

#     if kick_count<min_kicks:
#       return f"Your kick count is lower than expected for the {trimester} trimester. Please monitor and consult with your doctor if needed."
#     elif kick_count > max_kicks:
#         return f"Your kick count is higher than expected for the {trimester} trimester. Please consult with your doctor."
#     else:
#         return f"Your kick count is within the normal range for the {trimester} trimester."




# class BabyKickTrackingView(LoginRequiredMixin, View):
#     template_name = 'baby_kick_tracking.html'

#     def get(self, request, *args, **kwargs):
#         # Initial form rendering
#         form = BabyKickForm()
#         return render(request, self.template_name, {'form': form})

#     def post(self, request, *args, **kwargs):
#         form = BabyKickForm(request.POST)
#         if form.is_valid():
#             kick_data = form.save(commit=False)
#             kick_data.user = request.user
#             kick_data.date = timezone.now().date()
#             kick_data.save()

#             # Check if the kick count is within normal range for the trimester
#             message = check_kick_normality(kick_data)

#             # Render the form with the message
#             return render(request, self.template_name, {'form': form, 'message': message})

#         return render(request, self.template_name, {'form': form})



# diet plan

decs=[signin_required,never_cache]
@method_decorator(decs,name="dispatch")
class DietPlanListView(ListView):
    model = DietPlan
    template_name = 'diet_plans.html'  # Your template file
    context_object_name = 'diet_plans'

    def get_queryset(self):
        user = self.request.user  # Get the logged-in user
        try:
            # Access the related UserProfile
            user_profile = self.request.user.userprofile 

            trimester = user_profile.current_trimester

            # Filter diet plans based on the user's trimester
            return DietPlan.objects.filter(trimester=trimester)

        except UserProfile.DoesNotExist:
            # If no UserProfile exists for the logged-in user, you can return an empty queryset or show a message
            return DietPlan.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        try:
            user_profile = self.request.user.userprofile 
            context['trimester'] = user_profile.current_trimester
        except UserProfile.DoesNotExist:
            context['trimester'] = 'Unknown'  # Fallback in case of error
        return context



decs=[signin_required,never_cache]
@method_decorator(decs,name="dispatch")
class AboutusView(View):
    template_name='aboutus.html'
    def get(self,request,*args,**kwargs):

        return render(request,self.template_name)
    

from .models import ExerciseYoga



decs=[signin_required,never_cache]
@method_decorator(decs,name="dispatch")
class ExerciseYogaListView(ListView):
    model = ExerciseYoga
    template_name = 'exercise_yoga_list.html'  
    context_object_name = 'exercises'  

    def get_queryset(self):
        trimester = self.request.GET.get('trimester')
        
        if trimester:
            return ExerciseYoga.objects.filter(trimester=trimester)
        return ExerciseYoga.objects.all()


class LogOutView(View):

    def get (self,request,*args,**kwargs):

        logout(request)
        return redirect("frontpage")




# chatbot

import re
import groq
    
client =groq.Client(api_key="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")


def get_groq_response(user_input):
    """
    Communicate with the GROQ chatbot to get a response based on user input.
    """
    system_prompt = {
        "role": "system",
        "content": "You are a helpful assistant. You reply with very short answers ."
    }

    chat_history = [system_prompt]

    # Append user input to the chat history
    chat_history.append({"role": "user", "content": user_input})

    # Get response from GROQ API
    chat_completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=chat_history,
        max_tokens=100,
        temperature=1.2
    )

    response = chat_completion.choices[0].message.content
    print(response)
    # Format response (convert bold to <b>bold</b>)
    response = re.sub(r'\\(.?)\\*', r'<b>\1</b>', response)

    return response


import json
from django.http import JsonResponse

class ChatbotView(View):
    def get(self, request):
        return render(request, "chatbot.html")
    def post(self, request): 
        try:
            body = json.loads(request.body)
            user_input = body.get('userInput')
        except json.JSONDecodeError as e:
            return JsonResponse({"error": "Invalid JSON format."})
    
        if not user_input:  # If user_input is None or empty
            print("no")
            return JsonResponse({"error": "No user input provided."})  
        
        print("User Input:", user_input)
        
        static_responses = {
            "hi": "Hello! How can I assist you today?",
            "hello": "Hi there! How can I help you?",
            "how are you": "I'm just a chatbot, but I'm doing great! How about you?",
            "bye": "Goodbye! Take care.",
            "whats up": "Not much, just here to help you with  queries. How can I help you today?",
        }

        lower_input = user_input.lower().strip()
        if lower_input in static_responses:
            print(static_responses[lower_input])
            return JsonResponse({'response': static_responses[lower_input]})
        
        try:
            print("Processing via GROQ")
            data = get_groq_response(user_input)
            print(data)
            treatment_list = data.split('\n')
            return JsonResponse({'response': treatment_list})
        except Exception as e:
            return JsonResponse({"error": f"Failed to get GROQ response: {str(e)}"})




# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt  # ✅ Add this line
# import json
# from .chatbotlogic import get_bot_response 
# # Chatbot response view
# @csrf_exempt
# def chatbot_response(request):
#     if request.method == "POST":
#         user_input = request.POST.get('userInput', '')
#         bot_response = get_bot_response(user_input)  # Get AI response
#         return JsonResponse({"response": bot_response})

#     return JsonResponse({"response": "Invalid request"})

# # Render chat page
# def chatbot_page(request):
#     return render(request, 'chatbot.html')
