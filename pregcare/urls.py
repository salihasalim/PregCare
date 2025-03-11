"""
URL configuration for pregcare project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from care import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('shop/', include('ecommerce.urls', namespace='ecommerce')),
    path('',views.IndexPageView.as_view(),name='indexpage'),

    path('frontpage/',views.frontPageView.as_view(),name='frontpage'),
    path('home/',views.HomePageView.as_view(),name='home'),
    path('signup/',views.signUpView.as_view(),name='signup'),
    path('signin/',views.SignInView.as_view(),name='signin'),
    path('userprofile',views.user_profile,name='profile'),
    path('exerciseplan/',views.ExercisePlanView.as_view(),name='exercise_plan'),
    path('explore-books/', views.explore_books, name='explore_books'),
    path('download-book/<int:book_id>/', views.download_book, name='download_book'),
    path('reminders/add/', views.AddReminderView.as_view(), name='add_reminder'),
    path('reminders/', views.ReminderListView.as_view(), name='reminder_list'),
    path('reminders/mark_completed/<int:reminder_id>/', views.MarkAsCompletedView.as_view(), name='mark_as_completed'),
    path('pregnancytips',views.PregnancyTipsView.as_view(),name='pregnancytip'),
    # path('baby-kick-tracking/',views.BabyKickTrackingView.as_view(), name='baby_kick_tracking'),
     path('diet-plans/', views.DietPlanListView.as_view(), name='diet_plans'),
     path('exercise-yoga/',views.ExerciseYogaListView.as_view(), name='exercise_yoga_list'),

     path('aboutus',views.AboutusView.as_view(),name='aboutus'),
     path('logout/',views.LogOutView.as_view(),name='logout')




]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




