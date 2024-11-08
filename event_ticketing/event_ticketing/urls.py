"""
URL configuration for event_ticketing project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.generic.base import RedirectView
from . import views
from events import views
from events.views import profile_view, edit_event, delete_event
from django.contrib.auth import views as auth_views 
# from event.views import profile_view, edit_event, delete_event
# from event_ticketing.event.views import profile_view, edit_event, delete_event



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),

    # path('events/', views.event_list, name='event_list'), 
    # path('<int:event_id>/', views.event_detail, name='event_detail'),    
    path('events/', include('events.urls')),
    
    # path('', RedirectView.as_view(url='/events/', permanent=False)),
    path('', views.home, name='home'),
     
    # path('payments/', include('payments.urls')),
    path('payments/', include('payments.urls')),

    path('profile/', views.profile_view, name='profile'),
    path('add-event/', views.add_event, name='add_event'),
    path('edit-event/<int:event_id>/', edit_event, name='edit_event'),
    path('delete-event/<int:event_id>/', delete_event, name='delete_event'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
