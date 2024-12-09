from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from events import views as event_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', event_views.home, name='home'),
    path('accounts/', include('allauth.urls')),
    path('events/', include('events.urls')),
    path('payments/', include('payments.urls')),
    path('logout/', event_views.logout_view, name='logout'),
    path('logout/confirm/', event_views.logout_confirm, name='logout_confirm'),
    path('profile/', event_views.profile_view, name='profile'),
    path('add-event/', event_views.add_event, name='add_event'),
    path('edit-event/<int:event_id>/', event_views.edit_event, name='edit_event'),
    path('delete-event/<int:event_id>/', event_views.delete_event, name='delete_event'),
]


