# BiteTime

Live kitchen prep & order pipeline. A Django REST Framework backend that orchestrates the real-world workflow between **Customer**, **Waiter** and **Chef**: table check-in, ordering, kitchen queue, prep-time estimation, automatic status updates and email notifications.

## Tech Stack

- Python 3.14, Django 6.1, Django REST Framework
- PostgreSQL
- JWT authentication (`djangorestframework-simplejwt`)
- Celery + Redis (background jobs, Celery Beat schedules)
- MinIO / S3 via `boto3` (pre-signed URLs for heavy files)
- `drf-spectacular` (Swagger UI)
- `uv` for dependency management

## Features

- Custom user model with roles: `CUSTOMER`, `WAITER`, `CHEF` (plus `MANAGER` for administration)
- Role-based access control on every protected endpoint
- Order state machine: `PLACED → QUEUED → IN_PREP → READY → SERVED`
- Dynamic prep-time estimation
- Automatic `IN_PREP → READY` transition every 30 seconds
- Email notifications when an order enters `IN_PREP` and when it becomes `READY`
- Dual file handling: Django media uploads and S3/MinIO pre-signed URLs
- Daily cleanup job (archive served orders, expire pre-signed upload records)
- Kitchen capacity management command
- Audit logging middleware and token validity inspector

## Project Structure

```
core/               Django project (settings, urls, celery, exception handler)
common/
  models/           User, MenuItem, Order, OrderItem, TableCheckIn, PresignedUpload
  views/            API views
  serializers/      Request/response serializers
  permissions/      HasRole (role-based permission)
  components.py     Business logic (OrderService, TableService, MediaService, UserService)
  authentication.py TokenValidityInspector
  middleware.py     AuditLoggingMiddleware
  tasks.py          Celery tasks
  management/       calculate_kitchen_capacity, create_manager
Services/           Email and S3 helpers
logs/               audit.log, errors.log (generated)
media/              Uploaded thumbnails and avatars (generated)
```

## Getting Started

### 1. Prerequisites

- Python 3.14 and [uv](https://docs.astral.sh/uv/)
- PostgreSQL (running locally)
- Docker Desktop (for Redis and MinIO)

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `core.settings.development` (or `staging` / `production`) |
| `DEBUG` | `True` for local development |
| `SECRET_KEY` | Django secret key |
| `ALLOWED_HOSTS` | Comma-separated hosts, e.g. `127.0.0.1,localhost` |
| `DATABASE_URL` | e.g. `postgres://postgres:password@localhost:5432/bitetime` |
| `EMAIL_HOST_USER` | Gmail address used to send notifications |
| `EMAIL_HOST_PASSWORD` | Gmail **App Password** |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | MinIO/S3 credentials (`docker-compose.yml` also uses them as the MinIO root user/password) |
| `AWS_STORAGE_BUCKET_NAME` | Bucket name, default `bitetime-media` |
| `AWS_S3_ENDPOINT_URL` | `http://localhost:9000` for local MinIO |
| `AWS_S3_REGION_NAME` | e.g. `us-east-1` |

### 4. Create the database

Create an empty PostgreSQL database matching `DATABASE_URL` (for example `bitetime`), then:

```bash
uv run python manage.py migrate
```

### 5. Start Redis and MinIO

```bash
docker compose up -d
```

Open the MinIO console at http://localhost:9001, log in with your `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`, and **create a bucket** named `bitetime-media` (it is not created automatically).

### 6. Create a manager account

```bash
uv run python manage.py create_manager --username admin --email admin@example.com
```

You will be prompted for a password. The manager can create menu items and promote registered users to `CHEF` or `WAITER`.

### 7. Run the services

Use a separate terminal for each:

```bash
# API server
uv run python manage.py runserver

# Celery worker
uv run celery -A core worker -l info
# On Windows use the solo pool:
# uv run celery -A core worker -l info --pool=solo

# Celery Beat (schedules)
uv run celery -A core beat -l info
```

API docs (Swagger UI): http://127.0.0.1:8000/api/docs/

## Authentication & Roles

Log in to receive a JWT pair, then send the access token with every protected request:

```
Authorization: Bearer <access_token>
```

- Access token lifetime: 15 minutes
- Refresh token lifetime: 1 day (`/api/v1/auth/token/refresh/`)
- Registration always creates a `CUSTOMER`. Roles can only be changed by a `MANAGER` (to `CHEF` or `WAITER`).

All responses (except framework-level errors) use this envelope:

```json
{ "status": "success", "message": "...", "data": {}, "errors": null }
```

## API Endpoints

Base path: `/api/v1/`

| Method | Endpoint | Allowed roles | Description |
|---|---|---|---|
| POST | `register/` | Public | Customer registration |
| POST | `Login/` | Public | Login, returns JWT tokens |
| POST | `auth/token/refresh/` | Public | Refresh access token |
| GET | `menu/` | Authenticated | Browse menu and prep times (customers/waiters see available items only) |
| POST | `menu/` | Manager | Create menu item (multipart, supports `image`) |
| PATCH | `menu/{id}/toggle-availability/` | Chef | Toggle item availability |
| GET | `users/` | Manager | List users |
| PATCH | `users/{id}/role/` | Manager | Set role to `CHEF` or `WAITER` |
| PATCH | `users/me/avatar/` | Authenticated | Upload avatar (jpg/jpeg/png/webp, max 5 MB) |
| POST | `tables/check-in/` | Customer | Check in to a table |
| PATCH | `tables/check-out/` | Customer | Check out |
| POST | `orders/` | Customer | Place an order (requires active check-in) |
| GET | `orders/list/` | Authenticated | List orders (customers see only their own; archived hidden) |
| PATCH | `orders/{id}/queue/` | Waiter | `PLACED → QUEUED` |
| PATCH | `orders/{id}/start-prep/` | Chef | `QUEUED → IN_PREP`, sets ETA, sends email |
| PATCH | `orders/{id}/mark-ready/` | Chef | Manual override `IN_PREP → READY`, sends email |
| PATCH | `orders/{id}/served/` | Waiter | `READY → SERVED` |
| POST | `media/presigned-url/` | Waiter, Chef, Manager | Get a pre-signed **upload** URL |
| GET | `media/download-url/?object_key=...` | Authenticated | Get a pre-signed **download** URL |

Invalid state transitions return `409 Conflict`.

### Example: placing an order

```json
POST /api/v1/orders/
{
  "items": [
    { "menu_item": 1, "quantity": 2, "special_instructions": "no onions" },
    { "menu_item": 3 }
  ]
}
```

### Typical flow

1. Customer registers, logs in, checks in (`tables/check-in/`) and places an order.
2. Waiter sends it to the kitchen (`queue/`).
3. Chef starts prep (`start-prep/`); the customer receives an email with the estimated ready time.
4. When `now ≥ estimated_ready_at`, Celery Beat marks it `READY` automatically and emails the customer (the chef can also use `mark-ready/`).
5. Waiter marks it `SERVED`.

## Prep-Time Estimation

When the chef starts an order:

```
estimated_ready_at = max(now, latest estimated_ready_at of orders already IN_PREP)
                     + max(estimated_prep_minutes of the items in the order)
```

This models a kitchen that finishes orders one after another, so the backlog is the time until the last active order is done.

## Background Jobs (Celery Beat)

| Task | Schedule | What it does |
|---|---|---|
| `check_and_update_ready_orders` | Every 30 seconds | Moves overdue `IN_PREP` orders to `READY` and emails the customer |
| `daily_system_cleanup` | Daily at 00:00 UTC | Archives `SERVED` orders, marks expired pending pre-signed uploads as `EXPIRED`, deletes expired records older than 7 days |

## File Handling

**Server-side uploads (Django media)** — lightweight assets sent as multipart requests: menu item images and user avatars. Files are stored in `media/` and served at `/media/...` when `DEBUG=True`.

**Pre-signed URLs (S3/MinIO)** — heavy assets (videos, PDFs) go directly to object storage, bypassing the app server. Allowed content types: `video/mp4`, `video/quicktime`, `application/pdf`.

Upload flow:

1. `POST /api/v1/media/presigned-url/` with `{"file_name": "manual.pdf", "content_type": "application/pdf"}`. The response contains `upload_url` and `object_key`.
2. Upload the file straight to the returned URL. The `Content-Type` header must match the requested one:

```bash
curl -X PUT -H "Content-Type: application/pdf" --data-binary @manual.pdf "<upload_url>"
```

3. Download later with `GET /api/v1/media/download-url/?object_key=<object_key>` and open the returned `download_url`.

URLs expire after 1 hour.

## Management Commands

```bash
uv run python manage.py calculate_kitchen_capacity
```

Scans `IN_PREP` and `QUEUED` orders and prints the number of active orders, delayed orders, the average delay, and a warning when the kitchen is overloaded (more than 4 orders `IN_PREP`).

```bash
uv run python manage.py create_manager --username <name> --email <email>
```

Creates a `MANAGER` user (prompts for the password).

## Logging

- `logs/audit.log`: every request (method, path, user, status code, duration), order creation, status transitions and rejected tokens.
- `logs/errors.log`: errors.
