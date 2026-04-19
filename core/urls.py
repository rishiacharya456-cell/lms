from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('apps.accounts.urls')),
    path('', include('apps.dashboard.urls')),  # 🔥 THIS LINE MUST EXIST
    path('schools/', include('apps.schools.urls')),
    path('attendance/', include('attendance.urls')),
    path('courses/', include('apps.courses.urls')), 
    path('exams/', include('apps.exams.urls')),
    path('results/', include('apps.results.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)