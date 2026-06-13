from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from app.models import (
    Course, Lesson, LessonProgress, ActivityEvent,
    CollaborationSession, SharedNote, ChatMessage, Poll, PollResponse,
    Concept, Flashcard, LearningPath, PathOrder
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with sample data for all three challenges'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        # Create users
        self.create_users()
        
        # Challenge 1: Student Dashboard data
        self.create_courses_and_lessons()
        self.create_lesson_progress()
        self.create_activity_events()
        
        # Challenge 2: Collaboration data
        self.create_collaboration_sessions()
        
        # Challenge 3: Content data
        self.create_concepts_and_flashcards()
        self.create_learning_paths()
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))

    def create_users(self):
        self.stdout.write('Creating users...')
        
        # Create students
        for i in range(5):
            email = f'student{i}@example.com'
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    email=email,
                    password='password123',
                    role='student',
                    first_name=f'Student',
                    last_name=str(i + 1)
                )
        
        # Create mentors
        for i in range(2):
            email = f'mentor{i}@example.com'
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    email=email,
                    password='password123',
                    role='mentor',
                    first_name=f'Mentor',
                    last_name=str(i + 1)
                )
        
        self.stdout.write('Users created!')

    def create_courses_and_lessons(self):
        self.stdout.write('Creating courses and lessons...')
        
        courses_data = [
            {
                'title': 'Python Programming Fundamentals',
                'description': 'Learn the basics of Python programming from scratch',
                'lessons': [
                    ('Introduction to Python', 'Learn what Python is and why it\'s popular', 30),
                    ('Variables and Data Types', 'Understanding strings, integers, floats, and booleans', 45),
                    ('Control Flow', 'If statements, loops, and logical operators', 60),
                    ('Functions', 'Creating and using functions in Python', 50),
                    ('Lists and Dictionaries', 'Working with Python data structures', 55),
                ]
            },
            {
                'title': 'Web Development with Django',
                'description': 'Build web applications using the Django framework',
                'lessons': [
                    ('Django Setup', 'Installing and configuring Django', 40),
                    ('Models and Databases', 'Working with Django ORM', 60),
                    ('Views and URLs', 'Creating views and URL patterns', 50),
                    ('Templates', 'Building HTML templates with Django', 45),
                    ('Forms', 'Handling user input with Django forms', 55),
                ]
            },
            {
                'title': 'Data Science with Python',
                'description': 'Analyze data using Python libraries like pandas and numpy',
                'lessons': [
                    ('NumPy Basics', 'Numerical computing with NumPy', 45),
                    ('Pandas Fundamentals', 'Data manipulation with pandas', 60),
                    ('Data Visualization', 'Creating charts with matplotlib', 50),
                    ('Machine Learning Intro', 'Basic ML concepts with scikit-learn', 70),
                ]
            },
        ]
        
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                defaults={'description': course_data['description']}
            )
            
            for idx, (title, description, duration) in enumerate(course_data['lessons']):
                Lesson.objects.get_or_create(
                    course=course,
                    title=title,
                    defaults={
                        'description': description,
                        'order': idx,
                        'duration_minutes': duration
                    }
                )
        
        self.stdout.write('Courses and lessons created!')

    def create_lesson_progress(self):
        self.stdout.write('Creating lesson progress...')
        
        students = User.objects.filter(role='student')
        lessons = Lesson.objects.all()
        
        for student in students:
            for lesson in lessons:
                # Randomly decide if this lesson is completed
                if random.random() > 0.3:
                    completed = random.random() > 0.2
                    time_spent = random.randint(lesson.duration_minutes // 2, lesson.duration_minutes + 10)
                    
                    progress, created = LessonProgress.objects.get_or_create(
                        user=student,
                        lesson=lesson,
                        defaults={
                            'completed': completed,
                            'time_spent_minutes': time_spent,
                            'completed_at': timezone.now() - timedelta(days=random.randint(1, 30)) if completed else None
                        }
                    )
        
        self.stdout.write('Lesson progress created!')

    def create_activity_events(self):
        self.stdout.write('Creating activity events...')
        
        students = User.objects.filter(role='student')
        courses = Course.objects.all()
        
        for student in students:
            for _ in range(random.randint(5, 15)):
                event_type = random.choice([
                    'lesson_started', 'lesson_completed',
                    'course_started', 'course_completed',
                    'quiz_attempted', 'resource_accessed'
                ])
                
                course = random.choice(courses)
                lessons = list(course.lessons.all())
                lesson = random.choice(lessons) if lessons else None
                
                ActivityEvent.objects.create(
                    user=student,
                    event_type=event_type,
                    course=course,
                    lesson=lesson,
                    timestamp=timezone.now() - timedelta(days=random.randint(0, 30))
                )
        
        self.stdout.write('Activity events created!')

    def create_collaboration_sessions(self):
        self.stdout.write('Creating collaboration sessions...')
        
        users = list(User.objects.all())
        
        session_data = [
            ('Python Study Group', 'Weekly study session for Python learners'),
            ('Django Project Help', 'Get help with your Django projects'),
            ('Data Science Discussion', 'Discuss data science concepts and projects'),
        ]
        
        for name, description in session_data:
            host = random.choice(users)
            session, created = CollaborationSession.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'host': host
                }
            )
            
            if created:
                # Add random participants
                participants = random.sample([u for u in users if u != host], random.randint(2, 4))
                session.participants.set(participants)
                
                # Add some chat messages
                for _ in range(random.randint(3, 8)):
                    ChatMessage.objects.create(
                        session=session,
                        author=random.choice(participants + [host]),
                        message=random.choice([
                            'Can someone help me with this concept?',
                            'I think I understand now!',
                            'Let me share my notes.',
                            'Great question!',
                            'Here\'s a useful resource.',
                        ]),
                        created_at=timezone.now() - timedelta(minutes=random.randint(1, 60))
                    )
                
                # Add a poll
                poll = Poll.objects.create(
                    session=session,
                    question='What topic should we focus on next?',
                    options=['Functions', 'Classes', 'Modules', 'Testing']
                )
                
                # Add poll responses
                for participant in participants[:random.randint(1, len(participants))]:
                    PollResponse.objects.create(
                        poll=poll,
                        user=participant,
                        selected_option=random.randint(0, 3)
                    )
        
        self.stdout.write('Collaboration sessions created!')

    def create_concepts_and_flashcards(self):
        self.stdout.write('Creating concepts and flashcards...')
        
        concept_data = [
            ('Variables', 'Containers for storing data values', [
                ('What is a variable?', 'A named location used to store data in memory'),
                ('How do you declare a variable in Python?', 'Simply assign a value: x = 5'),
                ('What are the rules for variable names?', 'Must start with letter or underscore, no spaces'),
            ]),
            ('Functions', 'Reusable blocks of code', [
                ('What is a function?', 'A block of code that performs a specific task'),
                ('How do you define a function?', 'Use the def keyword: def my_function():'),
                ('What is a parameter?', 'A value passed to a function when it\'s called'),
            ]),
            ('Lists', 'Ordered collections of items', [
                ('What is a list?', 'An ordered collection that can hold multiple items'),
                ('How do you create a list?', 'Use square brackets: my_list = [1, 2, 3]'),
                ('How do you access list elements?', 'Use index: my_list[0] gets the first element'),
            ]),
            ('Dictionaries', 'Key-value pairs', [
                ('What is a dictionary?', 'A collection of key-value pairs'),
                ('How do you create a dictionary?', 'Use curly braces: my_dict = {"key": "value"}'),
                ('How do you access values?', 'Use the key: my_dict["key"]'),
            ]),
            ('Loops', 'Repeating code blocks', [
                ('What is a for loop?', 'Iterates over a sequence of elements'),
                ('What is a while loop?', 'Repeats while a condition is true'),
                ('How do you break out of a loop?', 'Use the break statement'),
            ]),
        ]
        
        for name, description, flashcards in concept_data:
            concept, created = Concept.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            
            for front, back in flashcards:
                Flashcard.objects.get_or_create(
                    concept=concept,
                    front=front,
                    defaults={'back': back, 'difficulty': random.randint(1, 3)}
                )
        
        self.stdout.write('Concepts and flashcards created!')

    def create_learning_paths(self):
        self.stdout.write('Creating learning paths...')
        
        # Create a Python learning path
        path, created = LearningPath.objects.get_or_create(
            name='Python Fundamentals Path',
            defaults={'description': 'A structured path to learn Python from basics to advanced'}
        )
        
        if created:
            concepts = Concept.objects.all()[:5]
            for idx, concept in enumerate(concepts):
                PathOrder.objects.create(
                    learning_path=path,
                    concept=concept,
                    order=idx
                )
        
        # Create a Web Development learning path
        path2, created = LearningPath.objects.get_or_create(
            name='Web Development Path',
            defaults={'description': 'Learn web development with Django'}
        )
        
        if created:
            concepts = Concept.objects.all()[2:5]
            for idx, concept in enumerate(concepts):
                PathOrder.objects.create(
                    learning_path=path2,
                    concept=concept,
                    order=idx
                )
        
        self.stdout.write('Learning paths created!')
