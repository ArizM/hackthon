from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
import json


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('mentor', 'Mentor'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    email = models.EmailField(unique=True)
    username = None  # Use email as username
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email


# Challenge 1: Progressive Student Dashboard Models
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField(default=0)
    duration_minutes = models.IntegerField(default=30)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class LessonProgress(models.Model):
    user = models.ForeignKey(User, related_name='lesson_progress', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='progress', on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    time_spent_minutes = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'lesson']
    
    def __str__(self):
        return f"{self.user.email} - {self.lesson.title}"


class ActivityEvent(models.Model):
    EVENT_TYPES = [
        ('lesson_started', 'Lesson Started'),
        ('lesson_completed', 'Lesson Completed'),
        ('course_started', 'Course Started'),
        ('course_completed', 'Course Completed'),
        ('quiz_attempted', 'Quiz Attempted'),
        ('resource_accessed', 'Resource Accessed'),
    ]
    
    user = models.ForeignKey(User, related_name='activity_events', on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    course = models.ForeignKey(Course, related_name='activity_events', on_delete=models.CASCADE, null=True, blank=True)
    lesson = models.ForeignKey(Lesson, related_name='activity_events', on_delete=models.CASCADE, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.email} - {self.event_type}"


# Challenge 2: Live Classroom Collaboration Models
class CollaborationSession(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    host = models.ForeignKey(User, related_name='hosted_sessions', on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name='joined_sessions', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name


class SharedNote(models.Model):
    session = models.ForeignKey(CollaborationSession, related_name='notes', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='shared_notes', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.session.name} - {self.author.email}"


class ChatMessage(models.Model):
    session = models.ForeignKey(CollaborationSession, related_name='chat_messages', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='chat_messages', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.session.name} - {self.author.email}"


class Poll(models.Model):
    session = models.ForeignKey(CollaborationSession, related_name='polls', on_delete=models.CASCADE)
    question = models.TextField()
    options = models.JSONField(default=list)  # List of option strings
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.session.name} - {self.question[:50]}"


class PollResponse(models.Model):
    poll = models.ForeignKey(Poll, related_name='responses', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='poll_responses', on_delete=models.CASCADE)
    selected_option = models.IntegerField()  # Index of selected option
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['poll', 'user']
    
    def __str__(self):
        return f"{self.poll.question[:30]} - {self.user.email}"


# Challenge 3: Multi-Source Learning Content Models
class UploadedFile(models.Model):
    FILE_TYPES = [
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
        ('txt', 'Text File'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, related_name='uploaded_files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    original_filename = models.CharField(max_length=255)
    file_size = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.original_filename


class ExtractedContent(models.Model):
    uploaded_file = models.ForeignKey(UploadedFile, related_name='extracted_contents', on_delete=models.CASCADE)
    content_type = models.CharField(max_length=50)  # 'text', 'transcript', 'metadata'
    content = models.TextField()
    extracted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.uploaded_file.original_filename} - {self.content_type}"


class Concept(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    parent_concept = models.ForeignKey('self', related_name='child_concepts', on_delete=models.CASCADE, null=True, blank=True)
    uploaded_files = models.ManyToManyField(UploadedFile, related_name='concepts', blank=True)
    
    def __str__(self):
        return self.name


class Flashcard(models.Model):
    uploaded_file = models.ForeignKey(UploadedFile, related_name='flashcards', on_delete=models.CASCADE)
    front = models.TextField()
    back = models.TextField()
    concept = models.ForeignKey(Concept, related_name='flashcards', on_delete=models.CASCADE, null=True, blank=True)
    difficulty = models.IntegerField(default=1)  # 1-5 scale
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.front[:50]}..."


class LearningPath(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    concepts = models.ManyToManyField(Concept, related_name='learning_paths', through='PathOrder')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class PathOrder(models.Model):
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        unique_together = ['learning_path', 'concept']
    
    def __str__(self):
        return f"{self.learning_path.name} - {self.concept.name}"
