from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from .forms import RatingForm,RatingUpdateForm, LoginForm, UserRegistrationForm, FreelancerRegistrationForm, ClientRegistrationForm, ProfileModelForm , ClientModelForm
from django.contrib.auth.decorators import login_required
from .models import Profile, Skill, Area, ConnectionRequest, Rating
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Model
from django.views.generic import ListView, UpdateView, DeleteView, DetailView
from django.contrib.auth.models import User
from django.db.models import Q
from posts.forms import PostModelForm, JobModelForm, CommentModelForm
from posts.models import Job, Post, Comment, JobRequest, JobAppointment
from django.urls import reverse_lazy


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'profiles/login.html', {'form': form})


@login_required
def dashboard(request):
    profile = Profile.objects.get(user=request.user)
    qs = Post.objects.filter(author=profile)
    connections = Profile.objects.get_all_friends_profile(request.user)
    if 'search_keyword' in request.GET:
        q = request.GET['search_keyword']
        all_posts = Post.objects.filter(content__icontains=q)
    else:
        all_posts = Post.objects.all()
    all_jobs = Job.objects.all()
    related_jobs = []
    connected_posts = []
    print("Connections of profile : ", profile)
    for post in all_posts:
        if post.author in connections:
            connected_posts.append(post)

    for job in all_jobs:
        if job.work_area == profile.work_area:
            related_jobs.append(job)


    post_form = PostModelForm()
    job_form = JobModelForm()
    comment_form = CommentModelForm()
    post_added = False
    job_added = False
    comment_added = False

    if 'submit_post_form' in request.POST:
        post_form = PostModelForm(request.POST, request.FILES)
        if post_form.is_valid():
            instance = post_form.save(commit=False)
            instance.author = profile
            instance.save()
            post_form = PostModelForm()
            post_added = True

    if 'submit_job_form' in request.POST:
        job_form = JobModelForm(request.POST, request.FILES)
        if job_form.is_valid():
            instance = job_form.save(commit=False)
            instance.author = profile
            instance.save()
            instance.title = job_form.cleaned_data.get('title')
            instance.description = job_form.cleaned_data.get('description')
            instance.image = job_form.cleaned_data.get('image')
            instance.work_area = job_form.cleaned_data.get('work_area')
            instance.skills.add(*job_form.cleaned_data.get('skills'))
            instance.salary = job_form.cleaned_data.get('salary')
            job_form = JobModelForm()
            job_added = True



    if 'submit_comment_form' in request.POST:
        comment_form = CommentModelForm(request.POST, request.FILES)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = profile
            comment.post = Post.objects.get(id=request.POST.get('post_id'))
            comment.save()
            comment_form = CommentModelForm()
            comment_added = False

    context = {
        'qs': qs,
        'profile': profile,
        'post_form': post_form,
        'comment_form': comment_form,
        'comment_added': comment_added,
        'post_added': post_added,
        'connections': connections,
        'connected_posts': connected_posts,
        'job_form': job_form,
        'job_added': job_added,
        'related_jobs': related_jobs,

    }
    return render(request, 'profiles/dashboard.html', context)


def register(request):
    if request.method == 'POST':
        print('Registering new user ')
        user_form = UserRegistrationForm(request.POST or None, request.FILES or None)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            print('Registration Successful!')
            return render(request, 'profiles/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'profiles/register.html', {'user_form': user_form})


def register_freelancer(request):
    if request.method == 'POST':
        print('Registering new user ')
        user_form = UserRegistrationForm(request.POST or None, request.FILES or None)
        profile_form = FreelancerRegistrationForm(request.POST or None, request.FILES or None)

        if user_form.is_valid() and profile_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            new_user.user_profile.is_freelancer = True
            new_user.user_profile.occupation = profile_form.cleaned_data.get('occupation')
            new_user.user_profile.education = profile_form.cleaned_data.get('education')
            new_user.user_profile.dp = profile_form.cleaned_data.get('dp')
            new_user.user_profile.cp = profile_form.cleaned_data.get('cp')
            new_user.user_profile.bio = profile_form.cleaned_data.get('bio')
            new_user.user_profile.phone_no = profile_form.cleaned_data.get('phone_no')
            new_user.user_profile.work_area = profile_form.cleaned_data.get('work_area')
            new_user.user_profile.skills.set(profile_form.cleaned_data.get('skills'))
            new_user.user_profile.pay_rate = profile_form.cleaned_data.get('pay_rate')
            new_user.user_profile.credit_card_no = profile_form.cleaned_data.get('credit_card_no')
            new_user.user_profile.save()
            return render(request, 'profiles/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
        profile_form = FreelancerRegistrationForm()

    return render(request, 'profiles/register_freelancer.html', {'user_form': user_form, 'profile_form': profile_form})


def register_client(request):
    if request.method == 'POST':
        print('Registering new user ')
        user_form = UserRegistrationForm(request.POST or None, request.FILES or None)
        profile_form = ClientRegistrationForm(request.POST or None, request.FILES or None)

        if user_form.is_valid() and profile_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            new_user.user_profile.is_client = True
            new_user.user_profile.occupation = profile_form.cleaned_data.get('occupation')
            new_user.user_profile.company = profile_form.cleaned_data.get('company')
            new_user.user_profile.dp = profile_form.cleaned_data.get('dp')
            new_user.user_profile.cp = profile_form.cleaned_data.get('cp')
            new_user.user_profile.bio = profile_form.cleaned_data.get('bio')
            new_user.user_profile.phone_no = profile_form.cleaned_data.get('phone_no')
            new_user.user_profile.phone_no = profile_form.cleaned_data.get('credit_card_no')

            new_user.user_profile.save()
            return render(request, 'profiles/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
        profile_form = ClientRegistrationForm()
    return render(request, 'profiles/register_client.html', {'user_form': user_form, 'profile_form': profile_form, })




@login_required
def profile_view(request, user_id):
    profile = Profile.objects.get(user=request.user)
    if profile.is_freelancer:
        form = ProfileModelForm(request.POST or None, request.FILES or None, instance=profile)
    else:
        form = ClientModelForm(request.POST or None, request.FILES or None, instance=profile)

    confirm = False
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            confirm = True
    context = {
        "profile": profile,
        "form": form,
        "confirm": confirm,

    }
    return render(request, 'profiles/profile.html', context)



def load_skills(request):
    area_id = request.GET.get('area')
    print(area_id)
    skills = Skill.objects.filter(area_id=area_id)
    print(skills)
    return render(request, 'profiles/skills_dropdown_list_options.html', {'skills': skills})


def connection_request_view(request):
    profile = Profile.objects.get(user=request.user)
    connections_requests = ConnectionRequest.objects.filter(receiver=profile, status='sent')
    jobs = Job.objects.filter(author=profile)
    job_requests = JobRequest.objects.filter(receiver=profile, status='applied')
    connections_requests = list(map(lambda x: x.sender, connections_requests))
    appointment_letters = JobAppointment.objects.filter(receiver=profile)
    is_empty = False
    if len(connections_requests) == 0:
        is_empty = True
    print(connections_requests)
    context = {
        'profile': profile,
        'connections_requests': connections_requests,
        'is_empty': is_empty,
        'jobs': jobs,
        'job_requests': job_requests,
        'appointment_letters': appointment_letters
    }
    return render(request, 'profiles/my_invites.html', context)


class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'profiles/detail.html'

    def get_object(self):
        id = self.kwargs.get('id')
        print(id)
        profile = Profile.objects.get(id=id)
        print(profile)
        return profile

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact = self.request.user)
        receiver_id = self.kwargs.get('id')
        rating_receiver = Profile.objects.get(id=receiver_id)
        can_rate = False
        profile = Profile.objects.get(user=user)
        profiles_employees = profile.get_employees()
        profile_employee_list = []
        for emp in profiles_employees:
            emp_profile = Profile.objects.get(user = emp)
            profile_employee_list.append(emp_profile)

        if rating_receiver in profile_employee_list:
            can_rate = True


        con_r = ConnectionRequest.objects.filter(sender=profile)
        con_s = ConnectionRequest.objects.filter(receiver=profile)
        score_sum = 0
        ratings = Rating.objects.filter(receiver=rating_receiver)
        print(ratings)
        print("*********")
        num_of_ratings = len(ratings)
        avg_rating = 0
        not_rated = False
        avg = []
        raters = []
        if num_of_ratings == 0:
            not_rated = True
        else:

            for rating in ratings:
                score_sum += rating.score
                raters.append(rating.sender)
            avg_rating = score_sum / num_of_ratings
            for i in range(int(avg_rating)):
                avg.append(1)

        con_receiver = []
        con_sender = []
        for item in con_r:
            con_receiver.append(item.receiver.user)
        for item in con_s:
            con_sender.append(item.sender.user)

        context["profile"] = profile
        context["con_receiver"] = con_receiver
        context["con_sender"] = con_sender
        context["receiver_id"] = receiver_id
        context["avg"] = avg
        context["not_rated"] = not_rated
        context["raters"] = raters
        context["can_rate"] = can_rate
        context['posts'] = self.get_object().get_posts()
        len_post = len(self.get_object().get_posts())
        is_empty = False
        if len_post == 0:
            is_empty = True
        context['is_empty'] = is_empty
        return context


class ProfileListView(ListView):
    model = Profile
    template_name = 'profiles/profile_list.html'
    context_object_name = 'qs'

    def get_queryset(self):
        qs = Profile.objects.get_all_profiles(self.request.user)
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact = self.request.user)
        profile = Profile.objects.get(user=user)
        con_r = ConnectionRequest.objects.filter(sender=profile)
        con_s = ConnectionRequest.objects.filter(receiver=profile)
        con_receiver = []
        con_sender = []
        for item in con_r:
            con_receiver.append(item.receiver.user)
        for item in con_s:
            con_sender.append(item.sender.user)

        context["profile"] = profile
        context["con_receiver"] = con_receiver
        context["con_sender"] = con_sender
        return context


def send_connection(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)
        connection = ConnectionRequest.objects.create(sender=sender, receiver=receiver, status='sent')
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:ProfileListView')


def remove_connection(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)
        connection = ConnectionRequest.objects.get(
            (Q(sender=sender) & Q(receiver=receiver)) | (Q(sender=receiver) & Q(receiver = sender))
        )
        connection.delete()
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:ProfileListView')


def approve_connection(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        receiver = Profile.objects.get(user=user)
        sender = Profile.objects.get(pk=pk)
        connection = get_object_or_404(ConnectionRequest, sender=sender, receiver=receiver)
        if connection.status == 'sent':
            connection.status = 'accepted'
            connection.save()
            receiver.connections.add(sender.user)
            sender.connections.add(receiver.user)
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:ProfileListView')


def connection_list(request):
    profile = Profile.objects.get(user=request.user)
    user = request.user

    connections = Profile.objects.get_all_friends_profile(user)
    print(connections)
    context= {
        'connections': connections,
        'profile': profile,
    }
    return render(request, 'profiles/connection_list.html', context)



def rating(request, user_id):
    profile = Profile.objects.get(id=user_id)
    sender = Profile.objects.get(user = request.user)
    profiles_ratings = Rating.objects.filter(sender=sender, receiver=profile)
    update = False
    profile_raters = []
    for rating in profiles_ratings:
        profile_raters.append(rating.sender)
    if sender in profile_raters:
        update = True

    if request.method == 'POST':
        if not update:
            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                new_rating = rating_form.save(commit=False)
                new_rating.receiver = profile
                new_rating.sender = sender
                new_rating.score = rating_form.cleaned_data.get('score')
                new_rating.save()
                return redirect('/')
        else:
            rating_form = RatingUpdateForm(request.POST)
            if rating_form.is_valid():
                new_rating = rating_form.save(commit=False)
                new_rating.receiver = profile
                new_rating.sender = sender
                new_rating.score = rating_form.cleaned_data.get('score')
                new_rating.save()
                return redirect('/')
    else:
        if not update:
            rating_form = RatingForm()
        else:
            rating_form = RatingUpdateForm()
    return render(request, "profiles/rating.html", {'rating_form': rating_form, 'update': update})


def all_ratings(request, user_id):
    profile = Profile.objects.get(id=user_id)
    all_ratings = Rating.objects.filter(receiver=profile)
    return render(request, "profiles/all_ratings.html", {'all_ratings': all_ratings , "profile": profile,})


def update_rating(request, user_id):
    rating_sender = Profile.objects.get(user = request.user)
    rating_receiver = Profile.objects.get(id=user_id)
    rating = Rating.objects.get(sender=rating_sender, receiver=rating_receiver)
    form = RatingForm(instance=rating)
    if request.method == 'POST':
        form = RatingForm(request.POST, instance=rating)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {
        'form': form,
    }
    return render(request, 'profiles/rating_update.html', context)