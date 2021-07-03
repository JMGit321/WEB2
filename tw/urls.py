"""tw URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns,static
from . import settings
from core import views
urlpatterns = [
    path('admin/', admin.site.urls),

    path('',views.home),

    path('galeria/',views.galeria),
    path('contato/',views.contato),
    path('postagens/',views.postagens),
    path('causas/',views.causas),
    path('causas/register/', views.register_cause),
    path('causas/register/submit', views.set_cause),
    path('galeria/delete/<id>', views.delete_cause),
    path('galeria/<id>/',views.single),
    path('galeria/<id>/submit', views.donate_cause),
    path('sobre/',views.sobre),
    path('sugestao/', views.sugestao),
    path('validar/', views.donates),
    path('validar/confirm/<id>', views.validate_donate),

    path('login/',views.login_user),
    path('login/submit', views.submit_login),
    path('logout/', views.logout_user),
    path('register/',views.register_user),
    path('profile/<id>/', views.profile),
    path('reset/', views.forgot_pass),
    path('reset/submit',views.reset_pass),
    path('reset/done/<id>/', views.confirm_reset, name="confirm_reset"),
    path('profile/delete/<id>/', views.delete_user),

    path('help/', views.help),
    path('completed/', views.completed_causes),

]
urlpatterns+=staticfiles_urlpatterns()
urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
urlpatterns+=static(settings.STATIC_URL,document_root=settings.STATICFILES_DIRS)
