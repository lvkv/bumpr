from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string

from .tokens import account_activation_token
from .forms import SignUpForm, PlateSearchForm, CommentForm
from .models import Plate, Comment

import logging


def index(request):
    return render(request, 'bumprapp/index.html', {})


def user_register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your MySite Account'
            message = render_to_string('registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('account_activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'bumprapp/user_register.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('index')
    else:
        return render(request, 'registration/account_activation_invalid.html')


def account_activation_sent(request):
    return render(request, 'registration/account_activation_sent.html', {})


@login_required
def user_profile(request, userstring):
    uid = get_object_or_404(User, username=request.user.username)
    profile_user = get_object_or_404(User, username=userstring)
    profile_user_plates = []
    for plate in Plate.objects.all().filter(driver=profile_user):
        profile_user_plates.append(plate)
    return render(request, 'bumprapp/user_profile.html',
                  {'user': uid, 'profile_user': profile_user, 'profile_user_plates': profile_user_plates})


@login_required
def user_profile_edit(request, userstring):
    if request.user.username != userstring:
        uid = get_object_or_404(User, username=request.user.username)
        profile_user = get_object_or_404(User, username=userstring)
        return render(request, 'bumprapp/user_profile.html', {'user': uid, 'profile_user': profile_user})
    uid = get_object_or_404(User, username=request.user.username)
    return render(request, 'bumprapp/user_profile_edit.html', {'user': uid})


@login_required
def user_settings(request):
    return render(request, 'bumprapp/user_settings.html', {})


def plate_url(request, pk):
    spec_plate = get_object_or_404(Plate, pk=pk)
    return render(request, 'bumprapp/plate_detail.html', {'spec_plate': spec_plate})


def plate_state(request, state_string):
    plate_list = get_list_or_404(Plate, state=state_string.upper())
    return render(request, 'bumprapp/plate_state.html', {'plate_list': plate_list,
                                                         's': state_string})


def plate_lookup(request):
    if request.method == 'POST':
        form = PlateSearchForm(request.POST)
        if form.is_valid():
            queryoni = form.cleaned_data.get('platetext')
            # stateroni = form.cleaned_data.get('statestring').upper()
            plateroni = form.cleaned_data.get('platetext')
            filtered_plates = Plate.objects.filter(plate_text__icontains=plateroni)
            return render(request, 'bumprapp/plate_search.html',
                          {'filtered_plates': filtered_plates, 'queryoni': queryoni})
    else:
        form = PlateSearchForm()
    states = Plate._meta.get_field('state').choices
    return render(request, 'bumprapp/plate_lookup.html', {'states': states, 'form': form})


def plate_detail(request, state_string, plate_string):
    spec_plate = get_object_or_404(Plate, plate_text=plate_string.upper(), state=state_string.upper())
    comment_form = CommentForm()
    comments_list = []

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = Comment(user=get_object_or_404(User, username=request.user.username), plate=spec_plate,
                                  comment_text=form.cleaned_data.get('commenttext'))
            new_comment.save()

    for comment in Comment.objects.all().filter(plate=spec_plate):
        comments_list.append(comment)

    return render(request, 'bumprapp/plate_detail.html',
                  {'spec_plate': spec_plate, 'comment_form': comment_form, 'comment_list': comments_list})
