from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from Home import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include("Home.urls")),
    path("product/", include("product.urls")),
    path("trial-item/", include("TrialItem.urls")),
    path("switch-language/<str:language_code>/", views.switch_language, name="switch_language"),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)