from django.contrib import admin

from .models import ExercisePlan,Book,PregnancyTip,DietPlan,ExerciseYoga
class ExerciseVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'trimester', 'description')  # Display these fields in the admin list view
    search_fields = ('title', 'description')  # Allow searching by title or description

class PregnancyTipAdmin(admin.ModelAdmin):
    list_display = ('trimester', 'tip_title', 'tip_description')  # Only show trimester, title, and description
    list_filter = ('trimester',)  # Filter by trimester only
    search_fields = ('tip_title', 'tip_description')  # Enable search by title and description
    ordering = ('trimester',)  # Default ordering by trimester

admin.site.register(ExercisePlan, ExerciseVideoAdmin)
admin.site.register(Book)
admin.site.register(PregnancyTip,PregnancyTipAdmin)
admin.site.register(DietPlan)
admin.site.register(ExerciseYoga)



