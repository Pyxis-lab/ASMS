from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import HttpResponseRedirect
from django.utils import translation
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme
import logging

logger = logging.getLogger(__name__)


def _safe_redirect_target(request, url, fallback):
    """Only allow redirects back to this site (prevents open redirects)."""
    if url and url_has_allowed_host_and_scheme(
        url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return url
    return fallback


def home(request):
    from product.models import AfterSalesRecord

    total = AfterSalesRecord.objects.count()
    resolved = AfterSalesRecord.objects.filter(resolved=True).count()
    stats = {
        'active_tickets': total - resolved,
        'resolution_rate': round(resolved * 100 / total) if total else 0,
        'customers': AfterSalesRecord.objects.exclude(user_name='').values('user_name').distinct().count(),
    }
    return render(request, "Home/home.html", {'stats': stats})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, _('Please enter both username and password.'))
            return render(request, 'Home/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                logger.info(f"User {username} logged in successfully")
                messages.success(request, _('Login successful!'))
                
                next_url = request.POST.get('next') or request.GET.get('next')
                return redirect(_safe_redirect_target(request, next_url, 'home'))
            else:
                messages.error(request, _('Your account is inactive.'))
                logger.warning(f"Login attempted for inactive user: {username}")
        else:
            messages.error(request, _('Invalid username or password.'))
            logger.warning(f"Failed login attempt for username: {username}")
    
    return render(request, 'Home/login.html')


def logout_view(request):
    if request.user.is_authenticated:
        logger.info(f"User {request.user.username} logged out")
        logout(request)
    
    messages.success(request, _('You have been logged out successfully.'))
    return redirect('login')


def switch_language(request, language_code):
    supported_langs = dict(settings.LANGUAGES)
    if language_code in supported_langs:
        translation.activate(language_code)
        response = HttpResponseRedirect(_safe_redirect_target(request, request.META.get('HTTP_REFERER'), '/'))
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            language_code,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            secure=settings.LANGUAGE_COOKIE_SECURE,
            httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
            samesite=settings.LANGUAGE_COOKIE_SAMESITE,
        )
        return response
    return HttpResponseRedirect(_safe_redirect_target(request, request.META.get('HTTP_REFERER'), '/'))


def about(request):
    return render(request, "Home/about.html")