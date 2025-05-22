from django.contrib import admin
from .models import Job, JobCategory, Application, User

class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    search_fields = ('name',)

class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'posted_by', 'location', 'is_active')
    list_filter = ('category', 'is_active', 'job_type')
    search_fields = ('title', 'description')
    raw_id_fields = ('posted_by', 'category')

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'applied_at', 'status')
    list_filter = ('status',)
    raw_id_fields = ('job', 'applicant')

# Register your models here
admin.site.register(JobCategory, JobCategoryAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(User)