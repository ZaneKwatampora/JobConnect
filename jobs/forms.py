from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Job, Application
from .models import Job, JobCategory
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'profile_picture',
            'first_name',
            'last_name',
            'bio',
            'location',
            'website',
            'github',
            'linkedin',
            'twitter'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class JobSeekerSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_job_seeker = True
        if commit:
            user.save()
        return user

class JobPosterSignUpForm(UserCreationForm):
    company_name = forms.CharField(max_length=100, required=True)
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'company_name')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_job_poster = True
        user.company_name = self.cleaned_data['company_name']
        if commit:
            user.save()
        return user

class JobForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = JobCategory.objects.all()
        self.fields['category'].empty_label = "Select a category"
        
    class Meta:
        model = Job
        fields = ['title', 'description', 'location', 'country', 'job_type', 'category', 'salary']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['resume', 'cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 5}),
        }
        labels = {
            'resume': 'Upload your resume',
            'cover_letter': 'Cover Letter',
        }
        
class ApplicationUpdateForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }