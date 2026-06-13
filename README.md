# Learning Platform - Full-Stack Hackathon Challenges

This project implements three comprehensive hackathon challenges in a single Django application:

1. **Progressive Student Dashboard** - Track student progress, visualize learning insights
2. **Live Classroom Collaboration Platform** - Real-time collaboration with WebSockets
3. **Multi-Source Learning Content Ingestion** - Parse files and generate structured learning artifacts

## Features

### Challenge 1: Progressive Student Dashboard
- Email authentication with student and mentor roles
- Dashboard showing completed lessons, time spent, progress per course
- Visualizations: Trend charts (time series) and pie/donut charts (distribution)
- Backend API for auth, aggregates, time-series data, lesson details, activity events
- Export to CSV functionality
- Seeded sample data

### Challenge 2: Live Classroom Collaboration Platform
- Real-time shared content (notes, chat, co-solving)
- Live feedback + polling with instant visualization
- Session persistence & exports
- Secure access control (participants only)
- Low-latency WebSocket sync
- Privacy-first design

### Challenge 3: Multi-Source Learning Content Ingestion
- Parse multiple file types (PDF, DOCX, TXT, Video, Audio)
- Extract key concepts + topic hierarchy
- Auto-generate structured educational outputs (flashcards, summaries)
- Store and enable retrieval by topic
- Export flashcards to JSON/CSV
- Concept graph and learning path generation

## Tech Stack

- **Backend**: Django 6.0.6, Django REST Framework
- **Real-time**: Django Channels (WebSockets)
- **Database**: SQLite (development)
- **Frontend**: HTML, CSS, JavaScript, Chart.js
- **File Processing**: PyPDF2, python-docx
- **Authentication**: Token-based auth

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
```bash
cd hacthonfullstack
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create a superuser (optional)**
```bash
python manage.py createsuperuser
```

6. **Seed the database with sample data**
```bash
python manage.py seed_data
```

This will create:
- 5 student accounts (student0@example.com to student4@example.com, password: password123)
- 2 mentor accounts (mentor0@example.com to mentor1@example.com, password: password123)
- 3 courses with lessons
- Lesson progress data
- Activity events
- Collaboration sessions with chat and polls
- Concepts and flashcards
- Learning paths

7. **Run the development server**
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

### Running with WebSockets (for Collaboration)

To enable real-time collaboration features, you need to run with an ASGI server:

```bash
pip install daphne
daphne hacthonfullstack.asgi:application
```

Or for development with channels:
```bash
python manage.py runserver
```

## Usage

### Accessing the Dashboard

1. Open `http://localhost:8000` in your browser
2. Register a new account or login with existing credentials
3. Navigate between the three tabs:
   - **Dashboard**: View progress stats, charts, and course progress
   - **Collaboration**: Create/join collaboration sessions, chat, polls
   - **Content Ingestion**: Upload files, view generated flashcards, export

### API Access

All API endpoints are documented in `API_DOCUMENTATION.md`

Example API usage:

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123","role":"student"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user@example.com","password":"password123"}'

# Get dashboard stats (with token)
curl -X GET http://localhost:8000/api/dashboard/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### Admin Panel

Access the Django admin panel at `http://localhost:8000/admin/` to manage all data.

## Project Structure

```
hacthonfullstack/
├── app/
│   ├── models.py              # Database models for all 3 challenges
│   ├── serializers.py         # DRF serializers
│   ├── views.py               # API views and frontend view
│   ├── urls.py                # App URL routes
│   ├── consumers.py           # WebSocket consumers
│   ├── routing.py             # WebSocket routing
│   ├── admin.py               # Admin configuration
│   ├── templates/
│   │   └── index.html         # Frontend dashboard
│   └── management/
│       └── commands/
│           └── seed_data.py   # Database seeding command
├── hacthonfullstack/
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URL routes
│   └── asgi.py                # ASGI configuration for WebSockets
├── requirements.txt           # Python dependencies
├── API_DOCUMENTATION.md       # Complete API documentation
└── README.md                  # This file
```

## API Endpoints Summary

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get token

### Challenge 1: Student Dashboard
- `GET/POST /api/courses/` - Manage courses
- `GET/POST /api/lessons/` - Manage lessons
- `GET/POST /api/lesson-progress/` - Track progress
- `POST /api/lesson-progress/update_progress/` - Update progress
- `GET/POST /api/activity-events/` - Activity events
- `GET /api/dashboard/` - Dashboard stats
- `GET /api/timeseries/` - Time-series data
- `GET /api/course-progress/` - Course progress
- `GET /api/export/csv/` - Export progress to CSV

### Challenge 2: Collaboration
- `GET/POST /api/collaboration-sessions/` - Manage sessions
- `POST /api/collaboration-sessions/{id}/join/` - Join session
- `POST /api/collaboration-sessions/{id}/leave/` - Leave session
- `POST /api/collaboration-sessions/{id}/end/` - End session
- `GET/POST /api/shared-notes/` - Shared notes
- `GET/POST /api/chat-messages/` - Chat messages
- `GET/POST /api/polls/` - Polls
- `POST /api/polls/{id}/vote/` - Vote on poll
- `GET /api/polls/{id}/results/` - Get poll results
- `WS /ws/collaboration/{session_id}/` - WebSocket connection

### Challenge 3: Content Ingestion
- `GET/POST /api/uploaded-files/` - Upload files
- `GET/POST /api/extracted-content/` - Extracted content
- `GET/POST /api/concepts/` - Concepts
- `GET/POST /api/flashcards/` - Flashcards
- `GET /api/flashcards/export_json/` - Export flashcards as JSON
- `GET /api/flashcards/export_csv/` - Export flashcards as CSV
- `GET/POST /api/learning-paths/` - Learning paths
- `GET /api/learning-paths/{id}/concepts/` - Path concepts

## Testing

### Manual Testing

1. **Dashboard**: Register/login, view stats, check charts
2. **Collaboration**: Create session, join, send chat messages, create poll, vote
3. **Content**: Upload file, view generated flashcards, export

### Automated Testing

Run tests with:
```bash
python manage.py test
```

## Deployment

### Environment Variables

Set these in production:
- `SECRET_KEY` - Django secret key
- `DEBUG=False` - Disable debug mode
- `ALLOWED_HOSTS` - Allowed hostnames
- `DATABASE_URL` - Production database URL
- `OPENAI_API_KEY` - For AI-powered content extraction (optional)

### Production Deployment

1. Set `DEBUG=False` in settings.py
2. Configure production database (PostgreSQL recommended)
3. Set up static file serving (whitenoise or CDN)
4. Use production ASGI server (daphne or uvicorn)
5. Configure Redis for channel layers (for production WebSockets)
6. Set up proper CORS settings
7. Use environment variables for sensitive data

## Stretch Features Implemented

✅ Email authentication with student/mentor roles
✅ Dashboard with completed lessons, time spent, progress per course
✅ Trend charts (time series) using Chart.js
✅ Pie/donut charts for distribution
✅ Backend API for auth, aggregates, time-series, lessons, activity
✅ Seeded sample data
✅ Export to CSV
✅ Real-time collaboration with WebSockets
✅ Shared notes with live sync
✅ Live polling with instant visualization
✅ Chat functionality
✅ Session persistence
✅ File upload support (PDF, DOCX, TXT, Video, Audio)
✅ Concept extraction
✅ Flashcard generation
✅ Export flashcards to JSON/CSV
✅ Learning path creation
✅ Concept graph hierarchy

## Future Enhancements

- AI-powered content extraction using OpenAI API
- Video/audio transcription
- Advanced analytics and recommendations
- Email notifications
- Mobile app
- Advanced permission system
- Real-time code collaboration
- Whiteboard feature
- Video conferencing integration

## License

This project is created for hackathon purposes.

## Support

For issues or questions, please refer to the API documentation or check the Django admin panel.
# hackthon
