from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from .forms import SignUpForm, EditProfileForm, EditUserForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_str
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import User, Profile
from datascraper.models import Location
from forum.models import Post

##################
# AUTHENTICATION #
##################


@transaction.atomic
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            group = Group.objects.get(name='Contribution')
            group.user_set.add(user)

            # sending activation email to new user
            current_site = get_current_site(request)
            subject = 'AGWeather Account Activation Link'
            message = render_to_string(
                'user_profile/account_activation_email.html',
                {'user': user,
                 'domain': current_site.domain,
                 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                 'token': account_activation_token.make_token(user),
                 })

            user.email_user(subject, message)

            return render(request, 'user_profile/account_activation_sent.html')
    else:
        return render(request, 'user_profile/signup.html')

    return render(request, 'user_profile/signup.html', {'form': form})


def activate(request, uidb64, token):

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'user_profile/account_activation_complete.html')
    else:
        return render(request, 'user_profile/account_activation_error.html')


@login_required
def profile(request, username):

    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)

    context = {
        'posts': Post.objects.filter(
            author=User.objects.get(username=username)),
        'profile': profile,
    }

    return render(request, 'user_profile/user_profile.html', context)


@login_required
def edit_user_profile(request, username):

    if username != request.user.username:
        return redirect('login')

    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)

    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=user)
        profile_form = EditProfileForm(
            request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('user_profile:profile', username)

    elif request.method == 'GET':
        user_form = EditUserForm(instance=user)
        profile_form = EditProfileForm(instance=profile)

    context = {'user_form': user_form,
               'profile_form': profile_form,
               'locations': Location.locations_list(),
               'avatar': profile.avatar.url, }

    return render(request, 'user_profile/edit_user_profile.html', context)
