from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import LogoutView

# 🔥 NEW IMPORTS (IMPORTANT)
from django.http import FileResponse, HttpResponseNotFound
import os


# 🔥 SERVICE WORKER VIEW
def firebase_sw(request):
    file_path = os.path.join(settings.BASE_DIR, "firebase-messaging-sw.js")

    if os.path.exists(file_path):
        return FileResponse(open(file_path, "rb"), content_type="application/javascript")
    else:
        return HttpResponseNotFound("Service worker not found")


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('apps.accounts.urls')),
    path('', include('apps.dashboard.urls')),  # 🔥 DASHBOARD
    path('schools/', include('apps.schools.urls')),
    path('attendance/', include('attendance.urls')),
    path('courses/', include('apps.courses.urls')), 
    path('exams/', include('apps.exams.urls')),
    path('results/', include('apps.results.urls')),
    path('communications/', include('apps.communications.urls')),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),

    # 🔥 ADD THIS LINE (CRITICAL)
    path('firebase-messaging-sw.js', firebase_sw),
]


# 🔥 MEDIA
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)