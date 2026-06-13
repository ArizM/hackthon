from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Sum, Q, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta, datetime
import csv
from django.http import HttpResponse

from .models import (
    User, Course, Lesson, LessonProgress, ActivityEvent,
    CollaborationSession, SharedNote, ChatMessage, Poll, PollResponse,
    UploadedFile, ExtractedContent, Concept, Flashcard, LearningPath, PathOrder
)
from .serializers import (
    UserSerializer, CourseSerializer, LessonSerializer, LessonProgressSerializer,
    ActivityEventSerializer, CollaborationSessionSerializer, SharedNoteSerializer,
    ChatMessageSerializer, PollSerializer, PollResponseSerializer,
    UploadedFileSerializer, ExtractedContentSerializer, ConceptSerializer,
    FlashcardSerializer, LearningPathSerializer, PathOrderSerializer,
    DashboardStatsSerializer, TimeSeriesDataSerializer, CourseProgressSerializer
)


# Challenge 1: Student Dashboard Views
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Lesson.objects.all()
        course_id = self.request.query_params.get('course', None)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset


class LessonProgressViewSet(viewsets.ModelViewSet):
    queryset = LessonProgress.objects.all()
    serializer_class = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = LessonProgress.objects.filter(user=self.request.user)
        course_id = self.request.query_params.get('course', None)
        if course_id:
            queryset = queryset.filter(lesson__course_id=course_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def update_progress(self, request):
        lesson_id = request.data.get('lesson_id')
        time_spent = request.data.get('time_spent', 0)
        completed = request.data.get('completed', False)
        
        try:
            progress = LessonProgress.objects.get(
                user=request.user, lesson_id=lesson_id
            )
            progress.time_spent_minutes += time_spent
            if completed and not progress.completed:
                progress.completed = True
                progress.completed_at = timezone.now()
                # Log activity event
                ActivityEvent.objects.create(
                    user=request.user,
                    event_type='lesson_completed',
                    lesson_id=lesson_id,
                    course_id=progress.lesson.course_id
                )
            progress.save()
            
            return Response(LessonProgressSerializer(progress).data)
        except LessonProgress.DoesNotExist:
            return Response(
                {'error': 'Progress record not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ActivityEventViewSet(viewsets.ModelViewSet):
    queryset = ActivityEvent.objects.all()
    serializer_class = ActivityEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ActivityEvent.objects.filter(user=self.request.user)
        days = self.request.query_params.get('days', None)
        if days:
            date_from = timezone.now() - timedelta(days=int(days))
            queryset = queryset.filter(timestamp__gte=date_from)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Calculate stats
        total_courses = Course.objects.count()
        completed_lessons = LessonProgress.objects.filter(
            user=user, completed=True
        ).count()
        total_lessons = Lesson.objects.count()
        total_time_spent = LessonProgress.objects.filter(
            user=user
        ).aggregate(total=Sum('time_spent_minutes'))['total'] or 0
        
        completion_percentage = (
            (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        )
        
        stats = DashboardStatsSerializer({
            'total_courses': total_courses,
            'completed_lessons': completed_lessons,
            'total_lessons': total_lessons,
            'total_time_spent': total_time_spent,
            'completion_percentage': round(completion_percentage, 2)
        })
        
        return Response(stats.data)


class TimeSeriesView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        days = int(request.query_params.get('days', 30))
        
        # Get daily activity data
        date_from = timezone.now() - timedelta(days=days)
        
        completed_lessons_data = ActivityEvent.objects.filter(
            user=user,
            event_type='lesson_completed',
            timestamp__gte=date_from
        ).annotate(
            date=TruncDate('timestamp')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        time_spent_data = LessonProgress.objects.filter(
            user=user,
            last_accessed__gte=date_from
        ).annotate(
            date=TruncDate('last_accessed')
        ).values('date').annotate(
            total=Sum('time_spent_minutes')
        ).order_by('date')
        
        # Combine data
        result = []
        date_dict = {}
        
        for item in completed_lessons_data:
            date_dict[str(item['date'])] = {
                'date': item['date'],
                'lessons_completed': item['count'],
                'time_spent_minutes': 0
            }
        
        for item in time_spent_data:
            date_str = str(item['date'])
            if date_str in date_dict:
                date_dict[date_str]['time_spent_minutes'] = item['total']
            else:
                date_dict[date_str] = {
                    'date': item['date'],
                    'lessons_completed': 0,
                    'time_spent_minutes': item['total']
                }
        
        result = list(date_dict.values())
        result.sort(key=lambda x: x['date'])
        
        return Response(result)


class CourseProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        courses = Course.objects.annotate(
            lesson_count=Count('lessons')
        ).all()
        
        result = []
        for course in courses:
            completed = LessonProgress.objects.filter(
                user=user,
                lesson__course=course,
                completed=True
            ).count()
            
            total = course.lesson_count
            progress = (completed / total * 100) if total > 0 else 0
            
            time_spent = LessonProgress.objects.filter(
                user=user,
                lesson__course=course
            ).aggregate(total=Sum('time_spent_minutes'))['total'] or 0
            
            result.append({
                'course_id': course.id,
                'course_title': course.title,
                'completed_lessons': completed,
                'total_lessons': total,
                'progress_percentage': round(progress, 2),
                'time_spent_minutes': time_spent
            })
        
        return Response(result)


class ExportCSVView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="progress_{user.email}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Course', 'Lesson', 'Completed', 'Time Spent (minutes)', 'Last Accessed'])
        
        progress_data = LessonProgress.objects.filter(user=user).select_related(
            'lesson', 'lesson__course'
        )
        
        for progress in progress_data:
            writer.writerow([
                progress.lesson.course.title,
                progress.lesson.title,
                progress.completed,
                progress.time_spent_minutes,
                progress.last_accessed
            ])
        
        return response


# Challenge 2: Collaboration Views
class CollaborationSessionViewSet(viewsets.ModelViewSet):
    queryset = CollaborationSession.objects.all()
    serializer_class = CollaborationSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(host=self.request.user)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        session = self.get_object()
        session.participants.add(request.user)
        return Response({'status': 'joined'})
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        session = self.get_object()
        session.participants.remove(request.user)
        return Response({'status': 'left'})
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        session = self.get_object()
        if session.host != request.user:
            return Response(
                {'error': 'Only host can end session'},
                status=status.HTTP_403_FORBIDDEN
            )
        session.is_active = False
        session.ended_at = timezone.now()
        session.save()
        return Response({'status': 'ended'})


class SharedNoteViewSet(viewsets.ModelViewSet):
    queryset = SharedNote.objects.all()
    serializer_class = SharedNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = SharedNote.objects.filter(
            session__participants=request.user
        )
        session_id = self.request.query_params.get('session', None)
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ChatMessage.objects.filter(
            session__participants=request.user
        )
        session_id = self.request.query_params.get('session', None)
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        return queryset.order_by('created_at')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Poll.objects.filter(
            session__participants=request.user
        )
        session_id = self.request.query_params.get('session', None)
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        poll = self.get_object()
        selected_option = request.data.get('selected_option')
        
        if selected_option is None:
            return Response(
                {'error': 'selected_option is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        response, created = PollResponse.objects.get_or_create(
            poll=poll,
            user=request.user,
            defaults={'selected_option': selected_option}
        )
        
        if not created:
            response.selected_option = selected_option
            response.save()
        
        return Response(PollResponseSerializer(response).data)
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        poll = self.get_object()
        responses = poll.responses.all()
        
        option_counts = {}
        for option in poll.options:
            option_counts[option] = 0
        
        for response in responses:
            option_index = response.selected_option
            if 0 <= option_index < len(poll.options):
                option_name = poll.options[option_index]
                option_counts[option_name] = option_counts.get(option_name, 0) + 1
        
        return Response({
            'question': poll.question,
            'options': poll.options,
            'results': option_counts,
            'total_votes': responses.count()
        })


# Challenge 3: Content Ingestion Views
class UploadedFileViewSet(viewsets.ModelViewSet):
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UploadedFile.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        file_obj = self.request.FILES.get('file')
        if file_obj:
            serializer.save(
                user=self.request.user,
                original_filename=file_obj.name,
                file_size=file_obj.size
            )


class ExtractedContentViewSet(viewsets.ModelViewSet):
    queryset = ExtractedContent.objects.all()
    serializer_class = ExtractedContentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ExtractedContent.objects.filter(
            uploaded_file__user=self.request.user
        )


class ConceptViewSet(viewsets.ModelViewSet):
    queryset = Concept.objects.all()
    serializer_class = ConceptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Concept.objects.filter(
            uploaded_files__user=self.request.user
        ).distinct()


class FlashcardViewSet(viewsets.ModelViewSet):
    queryset = Flashcard.objects.all()
    serializer_class = FlashcardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Flashcard.objects.filter(
            uploaded_file__user=self.request.user
        )
    
    @action(detail=False, methods=['get'])
    def export_json(self, request):
        flashcards = self.get_queryset()
        data = [
            {
                'front': card.front,
                'back': card.back,
                'concept': card.concept.name if card.concept else None,
                'difficulty': card.difficulty
            }
            for card in flashcards
        ]
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        flashcards = self.get_queryset()
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="flashcards.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Front', 'Back', 'Concept', 'Difficulty'])
        
        for card in flashcards:
            writer.writerow([
                card.front,
                card.back,
                card.concept.name if card.concept else '',
                card.difficulty
            ])
        
        return response


class LearningPathViewSet(viewsets.ModelViewSet):
    queryset = LearningPath.objects.all()
    serializer_class = LearningPathSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def concepts(self, request, pk=None):
        path = self.get_object()
        path_orders = PathOrder.objects.filter(
            learning_path=path
        ).select_related('concept').order_by('order')
        
        result = [
            {
                'concept_id': po.concept.id,
                'concept_name': po.concept.name,
                'description': po.concept.description,
                'order': po.order,
                'flashcard_count': po.concept.flashcards.count()
            }
            for po in path_orders
        ]
        
        return Response(result)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    email = request.data.get('email')
    password = request.data.get('password')
    role = request.data.get('role', 'student')
    
    if not email or not password:
        return Response(
            {'error': 'Email and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Email already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = User.objects.create_user(
        email=email,
        password=password,
        role=role
    )
    
    return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


def index_view(request):
    return render(request, 'index.html')
