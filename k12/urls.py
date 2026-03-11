
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500
from members import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('k12auth.urls')),
    path('', include('members.urls'))
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'members.views.error_404_view'
handler500 = 'members.views.error_500_view'