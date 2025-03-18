from django.db import models

from django.contrib.auth.models import User

# from embed_video.fields import EmbedVideoField

from django.core.exceptions import ValidationError

from django.utils import timezone

from datetime import date



class BaseModel(models.Model):

    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)



class UserProfile(BaseModel):

    lmp=models.DateField(blank=True,null=True)

    expected_due_date = models.DateField(null=True, blank=True)

    current_trimester = models.CharField(max_length=20,choices=[('First', 'First Trimester'), ('Second', 'Second Trimester'), ('Third', 'Third Trimester')], default='First')


    phone=models.CharField(max_length=200,null=True)

    mother=models.OneToOneField(User,on_delete=models.CASCADE)

    def clean(self):

         
        if self.lmp and self.lmp > timezone.now().date():
            raise ValidationError({'lmp': 'The LMP must be a past date.'})

       
        if self.expected_due_date and self.expected_due_date <= timezone.now().date():
            raise ValidationError({'expected_due_date': 'The expected due date must be a future date.'})

    def calculate_trimester(self):
        if self.lmp:
            today = date.today()
            days_pregnant = (today - self.lmp).days  # Calculate days since LMP

            # Trimester Calculation (approximate):
            if days_pregnant <= 90:  # First Trimester
                return 'First'
            elif 91 <= days_pregnant <= 180:  # Second Trimester
                return 'Second'
            elif days_pregnant > 180:  # Third Trimester
                return 'Third'
        return 'First'  # Default trimester if LMP is not provided

    def save(self, *args, **kwargs):
        self.current_trimester = self.calculate_trimester()  # Automatically set the trimester when saving
        super().save(*args, **kwargs)



    def __str__(self):
        return self.mother.username


from django.db.models.signals import post_save

def create_user_profile(sender,instance,created,**kwargs):

    if created:

        UserProfile.objects.create(mother=instance)

post_save.connect(create_user_profile,sender=User)



# EXRERCISE PLAN MODEL

class ExercisePlan(models.Model):
    TRIMESTER_CHOICES = [
        ('First', 'First Trimester'),
        ('Second', 'Second Trimester'),
        ('Third', 'Third Trimester'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    video_url = models.URLField()  # Store the URL of the exercise video
    trimester = models.CharField(choices=TRIMESTER_CHOICES, max_length=50)

    def __str__(self):
        return self.title


class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='book_covers/')
    book_file = models.FileField(upload_to='books/')  # For the downloadable book (PDF, EPUB, etc.)
    
    def __str__(self):
        return self.title



# for reminders

class Reminder(models.Model):
    REMINDER_TYPES = [
        ('appointment', 'Doctor Appointment'),
        ('medication', 'Medication Schedule'),
    ]

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    reminder_type = models.CharField(max_length=50, choices=REMINDER_TYPES)
    reminder_date = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    
    def str(self):
        return f"{self.title} ({self.reminder_type}) for {self.user.username}"

class PregnancyTip(models.Model):

       trimester = models.CharField(max_length=50)  # First, Second, Third
      
       tip_title = models.CharField(max_length=200)

       tip_description = models.TextField()

       def _str_(self):
           return self.tip_title



class BabyKickCount(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)

    date = models.DateField()

    kick_count = models.IntegerField()  

    # Number of kicks per day
    trimester = models.CharField(max_length=20, choices=[('First', 'First Trimester'), ('Second', 'Second Trimester'), ('Third', 'Third Trimester')])

    def _str_(self):
        return f"{self.user.username} - {self.date} - Kicks: {self.kick_count}"


class DietPlan(models.Model):

    trimester_choices = [
        ('First', 'First Trimester'),
        ('Second', 'Second Trimester'),
        ('Third', 'Third Trimester'),
    ]

    trimester = models.CharField(max_length=20, choices=trimester_choices)

    user = models.ForeignKey(User,on_delete=models.CASCADE)

    title = models.CharField(max_length=255)

    description = models.TextField()

    meal_plan = models.TextField() 
     # Detailed meal plan
    recommendations = models.TextField()  # Additional recommendations (e.g., foods to avoid, supplements)
    
    def __str__(self):

        return f"{self.trimester} - {self.title}"

    class Meta:

        ordering = ['trimester']






class ExerciseYoga(models.Model):
    TRIMESTER_CHOICES = [
        (1, "First Trimester"),
        (2, "Second Trimester"),
        (3, "Third Trimester"),
        (4, "Postpartum"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to="exercise_yoga/")
    trimester = models.IntegerField(choices=TRIMESTER_CHOICES)  # New field for filtering
    
    def __str__(self):
        return f"{self.name} ({self.get_trimester_display()})"