# Coffee Shop API

FastAPI-based user management system with authentication, authorization, and email verification.

## Features

- User registration and authentication with JWT (access + refresh tokens)
- Email verification (console-based for demo purposes)
- Role-based access control (User/Admin)
- Automatic cleanup of unverified users after 2 days (Celery)
- Async architecture with PostgreSQL
- Docker containerization

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy (async)
- **Authentication**: JWT (python-jose) + bcrypt
- **Task Queue**: Celery with Redis
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose installed

### Run the Application

```bash
# Clone the repository
git clone <repository-url>
cd coffee-shop-api

# Copy environment variables
cp .env.example .env

# Start all services
docker-compose up --build
```

The API will be available at `http://localhost:8000`

### API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Register a new user |
| POST | `/auth/login` | Login and get tokens |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/verify` | Verify email with code |

### User Management

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/me` | Get current user | Authenticated |
| GET | `/users` | List all users | Admin only |
| GET | `/users/{id}` | Get user by ID | Admin only |
| PATCH | `/users/{id}` | Update user | Owner or Admin |
| DELETE | `/users/{id}` | Delete user | Admin only |

## Project Architecture

```
app/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration and settings
├── database.py          # Async database connection
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── api/
│   ├── deps.py          # Dependencies (auth, DB session)
│   └── routes/          # API route handlers
├── core/
│   ├── security.py      # JWT and password utilities
│   └── roles.py         # Role-based access control
└── services/            # Business logic layer

celery_app/
├── celery.py            # Celery configuration
└── tasks.py             # Background tasks (user cleanup)
```

## Environment Variables

See `.env.example` for all available configuration options.

## Automatic User Cleanup

Unverified users are automatically deleted after 2 days via a Celery periodic task.
The task runs every hour and removes users where:
- `is_verified = false`
- `created_at < (now - 2 days)`

## Development Notes

### Simplifications Made

1. **Email Verification**: Verification codes are printed to console instead of being sent via email/SMS. 
   In production, this would integrate with an email service (SendGrid, AWS SES) or SMS provider (Twilio).

2. **Token Storage**: Refresh tokens are not stored server-side. 
   In production, you might want to store them in Redis for revocation capability.

## License

MIT
