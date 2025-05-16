from django.urls import path
from .views import HomeView, FileUploadView, ReportView, ReportListView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('upload/', FileUploadView.as_view(), name='upload'),
    path('report/<int:report_id>/', ReportView.as_view(), name='report'),
    path('reports/', ReportListView.as_view(), name='report_list'),
]

# Add media URL mappings in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)