from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .models import Job, Application, User, JobCategory
from .forms import JobSeekerSignUpForm, JobPosterSignUpForm, JobForm, ApplicationForm, ApplicationUpdateForm, JobSeekerProfileForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def home(request):
    jobs = Job.objects.filter(is_active=True).order_by('-created_at')[:10]
    return render(request, 'jobs/home.html', {
        'jobs': jobs,
        'categories': JobCategory.objects.all()
    })

def register(request):
    # New registration selection view
    return render(request, 'jobs/register.html')

def register_seeker(request):
    if request.method == 'POST':
        form = JobSeekerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Job seeker account created successfully!')
            return redirect('home')
    else:
        form = JobSeekerSignUpForm()
    return render(request, 'jobs/register_seeker.html', {
        'form': form,
        'user_type': 'seeker'
    })

def register_poster(request):
    if request.method == 'POST':
        form = JobPosterSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Employer account created successfully!')
            return redirect('home')
    else:
        form = JobPosterSignUpForm()
    return render(request, 'jobs/register_poster.html', {
        'form': form,
        'user_type': 'poster'
    })

@login_required
def post_job(request):
    if not request.user.is_job_poster:
        messages.error(request, 'Only employers can post jobs')
        return redirect('home')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('job_detail', job_id=job.id)
    else:
        form = JobForm()
    
    print("Categories available:", form['category'].field.queryset) 
    
    return render(request, 'jobs/post_job.html', {
        'form': form,
        'categories': JobCategory.objects.all()
    })

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    if not request.user.is_job_seeker:
        messages.error(request, 'Only job seekers can apply for jobs')
        return redirect('home')
    
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job')
        return redirect('job_detail', job_id=job.id)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('job_detail', job_id=job.id)
    else:
        form = ApplicationForm()
    
    return render(request, 'jobs/apply_job.html', {
        'form': form,
        'job': job
    })

@login_required
def my_jobs(request):
    if request.user.is_job_poster:
        jobs = Job.objects.filter(posted_by=request.user)
        return render(request, 'jobs/my_jobs.html', {
            'jobs': jobs,
            'is_poster': True
        })
    elif request.user.is_job_seeker:
        applications = Application.objects.filter(applicant=request.user).select_related('job')
        return render(request, 'jobs/my_jobs.html', {
            'applications': applications,
            'is_seeker': True
        })
    return redirect('home')

def job_detail(request, job_id):
    job = get_object_or_404(Job.objects.select_related('posted_by', 'category'), id=job_id)
    context = {
        'job': job,
        'can_apply': request.user.is_authenticated and request.user.is_job_seeker,
        'is_poster': request.user.is_authenticated and request.user == job.posted_by,
        'similar_jobs': Job.objects.filter(
            category=job.category,
            is_active=True
        ).exclude(id=job.id)[:4]
    }
    return render(request, 'jobs/job_detail.html', context)

def jobs_by_category(request, category_id):
    category = get_object_or_404(JobCategory, id=category_id)
    jobs = Job.objects.filter(
        category=category,
        is_active=True
    ).order_by('-created_at')
    
    return render(request, 'jobs/jobs_list.html', {
        'jobs': jobs,
        'category': category,
        'categories': JobCategory.objects.all()
    })
    
@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    if not request.user.is_job_seeker:
        messages.error(request, 'Only job seekers can apply for jobs')
        return redirect('home')
    
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job')
        return redirect('job_detail', job_id=job.id)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('job_detail', job_id=job.id)
    else:
        form = ApplicationForm()
    
    return render(request, 'jobs/apply_job.html', {
        'form': form,
        'job': job
    })
    
@login_required
def update_application(request, application_id):
    application = get_object_or_404(Application, id=application_id, job__posted_by=request.user)
    old_status = application.status  # Store the old status before any changes
    
    if request.method == 'POST':
        form = ApplicationUpdateForm(request.POST, instance=application)
        if form.is_valid():
            updated_application = form.save()
            
            # Check if status was changed
            if old_status != updated_application.status:
                send_status_update_email(updated_application)
                
            messages.success(request, 'Application updated successfully!')
            return redirect('job_applications', job_id=application.job.id)
    else:
        form = ApplicationUpdateForm(instance=application)
    
    return render(request, 'jobs/update_application.html', {
        'form': form,
        'application': application
    })

def send_status_update_email(application):
    subject = f"Update on your application for {application.job.title}"
    
    context = {
        'applicant': application.applicant,
        'job': application.job,
        'company': application.job.posted_by.company_name if hasattr(application.job.posted_by, 'company_name') else application.job.posted_by.username,
        'new_status': application.get_status_display(),
        'application_date': application.applied_at.strftime("%B %d, %Y"),
    }
    
    # Render both HTML and text versions
    html_message = render_to_string('emails/application_status_update.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email='noreply@yourdomain.com',
            recipient_list=[application.applicant.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        # Log the error if email sending fails
        print(f"Failed to send status update email: {e}")
    
@login_required
def job_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    applications = job.application_set.all().select_related('applicant')
    
    return render(request, 'jobs/job_applications.html', {
        'job': job,
        'applications': applications
    })
    
@login_required
def employer_dashboard(request):
    if not request.user.is_job_poster:
        return redirect('home')
    
    jobs = Job.objects.filter(posted_by=request.user).prefetch_related('application_set')
    return render(request, 'jobs/employer_dashboard.html', {'jobs': jobs})

@login_required
def view_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    applications = job.application_set.all().select_related('applicant')
    
    # Add status filtering
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    return render(request, 'jobs/view_applications.html', {
        'job': job,
        'applications': applications,
        'status_choices': Application.STATUS_CHOICES
    })

@login_required
def job_seeker_dashboard(request):
    if not request.user.is_job_seeker:
        return redirect('home')
    
    applications = Application.objects.filter(applicant=request.user).select_related('job')
    
    if request.method == 'POST':
        form = JobSeekerProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('job_seeker_dashboard')
    else:
        form = JobSeekerProfileForm(instance=request.user)
    
    return render(request, 'jobs/job_seeker_dashboard.html', {
        'applications': applications,
        'form': form
    })