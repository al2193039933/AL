# myproject/urls.py (This is your project's URL configuration file)
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from learning import views as learning_views

urlpatterns = [
	path('', learning_views.home, name='home'),
    path('admin/', admin.site.urls),
    path('learning/', include('learning.urls')) # Make sure this matches your app's name
    # ... other included URLs ...
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)