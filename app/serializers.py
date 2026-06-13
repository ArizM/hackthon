from rest_framework import serializers
from .models import (
    User, Course, Lesson, LessonProgress, ActivityEvent,
    CollaborationSession, SharedNote, ChatMessage, Poll, PollResponse,
    UploadedFile, ExtractedContent, Concept, Flashcard, LearningPath, PathOrder
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class LessonSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'course_title', 'title', 'description', 'order', 'duration_minutes']
        read_only_fields = ['id']


class LessonProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    course_title = serializers.CharField(source='lesson.course.title', read_only=True)
    
    class Meta:
        model = LessonProgress
        fields = ['id', 'user', 'lesson', 'lesson_title', 'course_title', 'completed', 
                  'time_spent_minutes', 'completed_at', 'last_accessed']
        read_only_fields = ['id', 'last_accessed']


class ActivityEventSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = ActivityEvent
        fields = ['id', 'user', 'user_email', 'event_type', 'course', 'course_title', 
                  'lesson', 'lesson_title', 'metadata', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class CollaborationSessionSerializer(serializers.ModelSerializer):
    host_email = serializers.CharField(source='host.email', read_only=True)
    participant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CollaborationSession
        fields = ['id', 'name', 'description', 'host', 'host_email', 'participant_count', 
                  'is_active', 'created_at', 'ended_at']
        read_only_fields = ['id', 'created_at', 'host']
    
    def get_participant_count(self, obj):
        return obj.participants.count()


class SharedNoteSerializer(serializers.ModelSerializer):
    author_email = serializers.CharField(source='author.email', read_only=True)
    
    class Meta:
        model = SharedNote
        fields = ['id', 'session', 'author', 'author_email', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatMessageSerializer(serializers.ModelSerializer):
    author_email = serializers.CharField(source='author.email', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'session', 'author', 'author_email', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


class PollSerializer(serializers.ModelSerializer):
    response_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Poll
        fields = ['id', 'session', 'question', 'options', 'is_active', 'response_count', 
                  'created_at', 'ended_at']
        read_only_fields = ['id', 'created_at']
    
    def get_response_count(self, obj):
        return obj.responses.count()


class PollResponseSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = PollResponse
        fields = ['id', 'poll', 'user', 'user_email', 'selected_option', 'created_at']
        read_only_fields = ['id', 'created_at']


class UploadedFileSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = UploadedFile
        fields = ['id', 'user', 'user_email', 'file', 'file_type', 'original_filename', 
                  'file_size', 'uploaded_at', 'processed']
        read_only_fields = ['id', 'uploaded_at']


class ExtractedContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedContent
        fields = ['id', 'uploaded_file', 'content_type', 'content', 'extracted_at']
        read_only_fields = ['id', 'extracted_at']


class ConceptSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent_concept.name', read_only=True)
    flashcard_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Concept
        fields = ['id', 'name', 'description', 'parent_concept', 'parent_name', 
                  'flashcard_count']
        read_only_fields = ['id']
    
    def get_flashcard_count(self, obj):
        return obj.flashcards.count()


class FlashcardSerializer(serializers.ModelSerializer):
    concept_name = serializers.CharField(source='concept.name', read_only=True)
    
    class Meta:
        model = Flashcard
        fields = ['id', 'uploaded_file', 'front', 'back', 'concept', 'concept_name', 
                  'difficulty', 'created_at']
        read_only_fields = ['id', 'created_at']


class LearningPathSerializer(serializers.ModelSerializer):
    concept_count = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPath
        fields = ['id', 'name', 'description', 'concept_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_concept_count(self, obj):
        return obj.concepts.count()


class PathOrderSerializer(serializers.ModelSerializer):
    concept_name = serializers.CharField(source='concept.name', read_only=True)
    
    class Meta:
        model = PathOrder
        fields = ['id', 'learning_path', 'concept', 'concept_name', 'order']
        read_only_fields = ['id']


class DashboardStatsSerializer(serializers.Serializer):
    total_courses = serializers.IntegerField()
    completed_lessons = serializers.IntegerField()
    total_lessons = serializers.IntegerField()
    total_time_spent = serializers.IntegerField()
    completion_percentage = serializers.FloatField()


class TimeSeriesDataSerializer(serializers.Serializer):
    date = serializers.DateField()
    lessons_completed = serializers.IntegerField()
    time_spent_minutes = serializers.IntegerField()


class CourseProgressSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    completed_lessons = serializers.IntegerField()
    total_lessons = serializers.IntegerField()
    progress_percentage = serializers.FloatField()
    time_spent_minutes = serializers.IntegerField()
