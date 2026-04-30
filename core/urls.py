from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

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

    # ✅ AUTH ROUTES (login, register etc.)
    path('', include('apps.accounts.urls')),   # handles /login/

    # ✅ MAIN HOMEPAGE (dashboard → /)
    path('', include('apps.dashboard.urls')),  

    # ✅ FEATURE MODULES
    path('schools/', include('apps.schools.urls')),
    path('attendance/', include('attendance.urls')),
    path('courses/', include('apps.courses.urls')), 
    path('exams/', include('apps.exams.urls')),
    path('results/', include('apps.results.urls')),
    path('communications/', include('apps.communications.urls')),
    path('syllabus/', include('apps.syllabus.urls')),
    path('missions/', include('apps.missions.urls')),
    path('assessments/', include('apps.assessments.urls')),
    path('dashboard/', include('apps.dashboard.urls')), 

    # ✅ LOGOUT
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),

    # ✅ SERVICE WORKER
    path('firebase-messaging-sw.js', firebase_sw),
]


# 🔥 MEDIA FILES
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)