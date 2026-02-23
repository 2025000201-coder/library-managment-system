from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .models import User
from .forms import LoginForm, RegisterForm, ProfileUpdateForm, UserEditForm


def log(user, action, desc, request=None):
    try:
        from activitylog.utils import log_activity
        log_activity(user, action, desc, request)
    except Exception:
        pass


# ─────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            log(user, 'user_login', f'{user.get_full_name()} logged in.', request)
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html', {'form': form})


# ─────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────
@login_required
def logout_view(request):
    log(request.user, 'user_logout', f'{request.user.get_full_name()} logged out.', request)
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


# ─────────────────────────────────────────
# REGISTER (Public)
# ─────────────────────────────────────────
def register_view(request):
    # If logged in as admin/librarian → allow adding users
    # If logged in as student → redirect to dashboard
    # If not logged in → show public register page
    if request.user.is_authenticated:
        if not (request.user.is_admin_user or request.user.is_librarian_user):
            return redirect('dashboard:home')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            if request.user.is_authenticated:
                messages.success(request, f'User "{user.get_full_name()}" created successfully!')
                return redirect('accounts:user_list')
            else:
                login(request, user)
                messages.success(request, f'Welcome, {user.get_full_name()}! Account created successfully!')
                return redirect('dashboard:home')

    return render(request, 'accounts/register.html', {'form': form})


# ─────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────
@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


# ─────────────────────────────────────────
# EDIT PROFILE
# ─────────────────────────────────────────
@login_required
def edit_profile_view(request):
    form = ProfileUpdateForm(request.POST or None,
                             request.FILES or None,
                             instance=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            log(request.user, 'user_edited', f'{request.user.get_full_name()} updated their profile.', request)
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')

    return render(request, 'accounts/edit_profile.html', {'form': form})


# ─────────────────────────────────────────
# CHANGE PASSWORD
# ─────────────────────────────────────────
@login_required
def change_password_view(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            log(request.user, 'user_edited', f'{request.user.get_full_name()} changed their password.', request)
            messages.success(request, 'Password changed successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please fix the errors below.')

    return render(request, 'accounts/change_password.html', {'form': form})


# ─────────────────────────────────────────
# USER LIST
# ─────────────────────────────────────────
@login_required
def user_list_view(request):
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    users = User.objects.all().order_by('-created_at')
    return render(request, 'accounts/user_list.html', {'users': users})


# ─────────────────────────────────────────
# EDIT USER
# ─────────────────────────────────────────
@login_required
def user_edit_view(request, pk):
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    user = get_object_or_404(User, pk=pk)
    form = UserEditForm(request.POST or None, instance=user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            log(request.user, 'user_edited', f'Admin edited user: {user.get_full_name()}', request)
            messages.success(request, f'User "{user.username}" updated successfully!')
            return redirect('accounts:user_list')

    return render(request, 'accounts/user_edit.html', {'form': form, 'edit_user': user})


# ─────────────────────────────────────────
# DELETE USER
# ─────────────────────────────────────────
@login_required
def user_delete_view(request, pk):
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        username = user.username
        fullname = user.get_full_name()
        user.delete()
        log(request.user, 'user_deleted', f'Admin deleted user: {fullname} ({username})', request)
        messages.success(request, f'User "{username}" deleted successfully!')
        return redirect('accounts:user_list')

    return render(request, 'accounts/user_confirm_delete.html', {'edit_user': user})