# API Documentation

## Overview
This API provides endpoints for three main challenges:
1. Progressive Student Dashboard
2. Live Classroom Collaboration Platform
3. Multi-Source Learning Content Ingestion

## Authentication
All endpoints (except registration) require authentication via Token Authentication.

### Register
```http
POST /api/auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "role": "student"  // or "mentor"
}
```

### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}

Response:
{
  "token": "abc123..."
}
```

### Using the Token
Include the token in the Authorization header:
```
Authorization: Token abc123...
```

---

## Challenge 1: Student Dashboard

### Courses
```http
GET /api/courses/
POST /api/courses/
PUT /api/courses/{id}/
DELETE /api/courses/{id}/
```

**Course Object:**
```json
{
  "id": 1,
  "title": "Python Programming",
  "description": "Learn Python from scratch",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Lessons
```http
GET /api/lessons/?course={course_id}
POST /api/lessons/
PUT /api/lessons/{id}/
DELETE /api/lessons/{id}/
```

**Lesson Object:**
```json
{
  "id": 1,
  "course": 1,
  "course_title": "Python Programming",
  "title": "Introduction to Python",
  "description": "Learn the basics",
  "order": 0,
  "duration_minutes": 30
}
```

### Lesson Progress
```http
GET /api/lesson-progress/?course={course_id}
POST /api/lesson-progress/
PUT /api/lesson-progress/{id}/
DELETE /api/lesson-progress/{id}/
POST /api/lesson-progress/update_progress/
```

**Update Progress:**
```json
{
  "lesson_id": 1,
  "time_spent": 15,
  "completed": true
}
```

**Progress Object:**
```json
{
  "id": 1,
  "user": 1,
  "lesson": 1,
  "lesson_title": "Introduction to Python",
  "course_title": "Python Programming",
  "completed": true,
  "time_spent_minutes": 45,
  "completed_at": "2024-01-01T00:00:00Z",
  "last_accessed": "2024-01-01T00:00:00Z"
}
```

### Activity Events
```http
GET /api/activity-events/?days={days}
POST /api/activity-events/
```

**Activity Event Object:**
```json
{
  "id": 1,
  "user": 1,
  "user_email": "user@example.com",
  "event_type": "lesson_completed",
  "course": 1,
  "course_title": "Python Programming",
  "lesson": 1,
  "lesson_title": "Introduction to Python",
  "metadata": {},
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Dashboard Stats
```http
GET /api/dashboard/
```

**Response:**
```json
{
  "total_courses": 3,
  "completed_lessons": 15,
  "total_lessons": 20,
  "total_time_spent": 450,
  "completion_percentage": 75.0
}
```

### Time Series Data
```http
GET /api/timeseries/?days={days}
```

**Response:**
```json
[
  {
    "date": "2024-01-01",
    "lessons_completed": 2,
    "time_spent_minutes": 60
  }
]
```

### Course Progress
```http
GET /api/course-progress/
```

**Response:**
```json
[
  {
    "course_id": 1,
    "course_title": "Python Programming",
    "completed_lessons": 5,
    "total_lessons": 10,
    "progress_percentage": 50.0,
    "time_spent_minutes": 150
  }
]
```

### Export CSV
```http
GET /api/export/csv/
```
Returns a CSV file with progress data.

---

## Challenge 2: Collaboration Platform

### Collaboration Sessions
```http
GET /api/collaboration-sessions/
POST /api/collaboration-sessions/
PUT /api/collaboration-sessions/{id}/
DELETE /api/collaboration-sessions/{id}/
POST /api/collaboration-sessions/{id}/join/
POST /api/collaboration-sessions/{id}/leave/
POST /api/collaboration-sessions/{id}/end/
```

**Session Object:**
```json
{
  "id": 1,
  "name": "Python Study Group",
  "description": "Weekly study session",
  "host": 1,
  "host_email": "mentor@example.com",
  "participant_count": 5,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "ended_at": null
}
```

### Shared Notes
```http
GET /api/shared-notes/?session={session_id}
POST /api/shared-notes/
PUT /api/shared-notes/{id}/
DELETE /api/shared-notes/{id}/
```

**Note Object:**
```json
{
  "id": 1,
  "session": 1,
  "author": 1,
  "author_email": "user@example.com",
  "content": "Notes from the session...",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Chat Messages
```http
GET /api/chat-messages/?session={session_id}
POST /api/chat-messages/
```

**Chat Message Object:**
```json
{
  "id": 1,
  "session": 1,
  "author": 1,
  "author_email": "user@example.com",
  "message": "Hello everyone!",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Polls
```http
GET /api/polls/?session={session_id}
POST /api/polls/
PUT /api/polls/{id}/
DELETE /api/polls/{id}/
POST /api/polls/{id}/vote/
GET /api/polls/{id}/results/
```

**Create Poll:**
```json
{
  "session": 1,
  "question": "What topic should we cover next?",
  "options": ["Functions", "Classes", "Modules"]
}
```

**Vote:**
```json
{
  "selected_option": 0
}
```

**Poll Object:**
```json
{
  "id": 1,
  "session": 1,
  "question": "What topic should we cover next?",
  "options": ["Functions", "Classes", "Modules"],
  "is_active": true,
  "response_count": 5,
  "created_at": "2024-01-01T00:00:00Z",
  "ended_at": null
}
```

**Poll Results:**
```json
{
  "question": "What topic should we cover next?",
  "options": ["Functions", "Classes", "Modules"],
  "results": {
    "Functions": 3,
    "Classes": 1,
    "Modules": 1
  },
  "total_votes": 5
}
```

### WebSocket Connection
```
ws://localhost:8000/ws/collaboration/{session_id}/
```

**WebSocket Messages:**
```json
// Send chat message
{
  "type": "chat_message",
  "message": "Hello!"
}

// Update note
{
  "type": "note_update",
  "content": "Updated notes..."
}

// Create poll
{
  "type": "poll_create",
  "question": "Question?",
  "options": ["Option 1", "Option 2"]
}

// Vote on poll
{
  "type": "poll_vote",
  "poll_id": 1,
  "selected_option": 0
}
```

---

## Challenge 3: Content Ingestion

### Uploaded Files
```http
GET /api/uploaded-files/
POST /api/uploaded-files/
PUT /api/uploaded-files/{id}/
DELETE /api/uploaded-files/{id}/
```

**Upload File (multipart/form-data):**
```
file: <binary data>
file_type: "pdf" | "docx" | "txt" | "video" | "audio" | "other"
```

**File Object:**
```json
{
  "id": 1,
  "user": 1,
  "user_email": "user@example.com",
  "file": "/uploads/file.pdf",
  "file_type": "pdf",
  "original_filename": "document.pdf",
  "file_size": 1024000,
  "uploaded_at": "2024-01-01T00:00:00Z",
  "processed": false
}
```

### Extracted Content
```http
GET /api/extracted-content/
POST /api/extracted-content/
PUT /api/extracted-content/{id}/
DELETE /api/extracted-content/{id}/
```

**Extracted Content Object:**
```json
{
  "id": 1,
  "uploaded_file": 1,
  "content_type": "text",
  "content": "Extracted text content...",
  "extracted_at": "2024-01-01T00:00:00Z"
}
```

### Concepts
```http
GET /api/concepts/
POST /api/concepts/
PUT /api/concepts/{id}/
DELETE /api/concepts/{id}/
```

**Concept Object:**
```json
{
  "id": 1,
  "name": "Variables",
  "description": "Containers for storing data values",
  "parent_concept": null,
  "parent_name": null,
  "flashcard_count": 3
}
```

### Flashcards
```http
GET /api/flashcards/
POST /api/flashcards/
PUT /api/flashcards/{id}/
DELETE /api/flashcards/{id}/
GET /api/flashcards/export_json/
GET /api/flashcards/export_csv/
```

**Flashcard Object:**
```json
{
  "id": 1,
  "uploaded_file": 1,
  "front": "What is a variable?",
  "back": "A named location used to store data",
  "concept": 1,
  "concept_name": "Variables",
  "difficulty": 2,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Learning Paths
```http
GET /api/learning-paths/
POST /api/learning-paths/
PUT /api/learning-paths/{id}/
DELETE /api/learning-paths/{id}/
GET /api/learning-paths/{id}/concepts/
```

**Learning Path Object:**
```json
{
  "id": 1,
  "name": "Python Fundamentals Path",
  "description": "Structured path to learn Python",
  "concept_count": 5,
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Learning Path Concepts:**
```json
[
  {
    "concept_id": 1,
    "concept_name": "Variables",
    "description": "Containers for storing data values",
    "order": 0,
    "flashcard_count": 3
  }
]
```

---

## Error Responses

All endpoints may return error responses:

```json
{
  "error": "Error message here"
}
```

Common HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Server Error
