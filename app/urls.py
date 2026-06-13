from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as auth_views
from .views import (
    CourseViewSet, LessonViewSet, LessonProgressViewSet, ActivityEventViewSet,
    CollaborationSessionViewSet, SharedNoteViewSet, ChatMessageViewSet, PollViewSet,
    UploadedFileViewSet, ExtractedContentViewSet, ConceptViewSet, FlashcardViewSet,
    LearningPathViewSet, DashboardView, TimeSeriesView, CourseProgressView,
    ExportCSVView, register, index_view
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'lesson-progress', LessonProgressViewSet)
router.register(r'activity-events', ActivityEventViewSet)
router.register(r'collaboration-sessions', CollaborationSessionViewSet)
router.register(r'shared-notes', SharedNoteViewSet)
router.register(r'chat-messages', ChatMessageViewSet)
router.register(r'polls', PollViewSet)
router.register(r'uploaded-files', UploadedFileViewSet)
router.register(r'extracted-content', ExtractedContentViewSet)
router.register(r'concepts', ConceptViewSet)
router.register(r'flashcards', FlashcardViewSet)
router.register(r'learning-paths', LearningPathViewSet)

urlpatterns = [
    path('', index_view, name='index'),
    path('api/', include(router.urls)),
    path('api/auth/login/', auth_views.obtain_auth_token),
    path('api/auth/register/', register),
    path('api/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('api/timeseries/', TimeSeriesView.as_view(), name='timeseries'),
    path('api/course-progress/', CourseProgressView.as_view(), name='course-progress'),
    path('api/export/csv/', ExportCSVView.as_view(), name='export-csv'),
]
