from django.contrib import admin
from .models import (
    User, Course, Lesson, LessonProgress, ActivityEvent,
    CollaborationSession, SharedNote, ChatMessage, Poll, PollResponse,
    UploadedFile, ExtractedContent, Concept, Flashcard, LearningPath, PathOrder
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'role', 'is_staff', 'date_joined']
    list_filter = ['role', 'is_staff']
    search_fields = ['email']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    search_fields = ['title', 'description']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'duration_minutes']
    list_filter = ['course']
    search_fields = ['title']


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'completed', 'time_spent_minutes']
    list_filter = ['completed']
    search_fields = ['user__email', 'lesson__title']


@admin.register(ActivityEvent)
class ActivityEventAdmin(admin.ModelAdmin):
    list_display = ['user', 'event_type', 'timestamp']
    list_filter = ['event_type', 'timestamp']
    search_fields = ['user__email']


@admin.register(CollaborationSession)
class CollaborationSessionAdmin(admin.ModelAdmin):
    list_display = ['name', 'host', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(SharedNote)
class SharedNoteAdmin(admin.ModelAdmin):
    list_display = ['session', 'author', 'created_at']
    list_filter = ['session']
    search_fields = ['content']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'author', 'created_at']
    list_filter = ['session']
    search_fields = ['message']


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ['session', 'question', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['question']


@admin.register(PollResponse)
class PollResponseAdmin(admin.ModelAdmin):
    list_display = ['poll', 'user', 'selected_option']
    list_filter = ['poll']


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'file_type', 'user', 'processed']
    list_filter = ['file_type', 'processed']
    search_fields = ['original_filename']


@admin.register(ExtractedContent)
class ExtractedContentAdmin(admin.ModelAdmin):
    list_display = ['uploaded_file', 'content_type', 'extracted_at']
    list_filter = ['content_type']


@admin.register(Concept)
class ConceptAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent_concept']
    search_fields = ['name', 'description']


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ['front', 'concept', 'difficulty']
    list_filter = ['difficulty']
    search_fields = ['front']


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(PathOrder)
class PathOrderAdmin(admin.ModelAdmin):
    list_display = ['learning_path', 'concept', 'order']
    list_filter = ['learning_path']
