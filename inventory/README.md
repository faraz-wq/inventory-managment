# Asset Verification & Management System

A comprehensive Django REST Framework backend for managing departments, users, roles, permissions, and physical assets with geographic tracking.

## Features

- JWT-based authentication
- Role-Based Access Control (RBAC)
- Department and user management
- Geographic location hierarchy (District > Mandal > Village)
- Item catalogue and inventory tracking
- Dynamic item attributes
- Automatic activity logging
- RESTful API with filtering, search, and pagination
- Swagger/OpenAPI documentation

## Tech Stack

- Django 5.0.1
- Django REST Framework 3.14.0
- PostgreSQL
- JWT Authentication (SimpleJWT)
- Swagger/OpenAPI (drf-yasg)
- Django Filters & CORS Headers

## Project Structure

```
inventory/
├── manage.py
├── requirements.txt
├── README.md
├── .env.example
├── backend/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── apps/
    ├── users/          # User management & authentication
    ├── departments/    # Department & contacts
    ├── rbac/          # Roles & permissions
    ├── items/         # Item tracking & attributes
    ├── locations/     # District/Mandal/Village hierarchy
    ├── logs/          # Activity logging
    └── catalogue/     # Item definitions (master data)
```

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

### Step 1: Clone or Navigate to Project

```bash
cd inventory
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Database

Create a PostgreSQL database:

```sql
CREATE DATABASE asset_management;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE asset_management TO postgres;
```

### Step 5: Environment Configuration

Copy `.env.example` to `.env` and update values:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` with your settings:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=asset_management
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Step 6: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 7: Create Superuser

```bash
python manage.py createsuperuser
```

Follow prompts to create admin account.

### Step 8: Run Development Server

```bash
python manage.py runserver
```

Server will start at `http://127.0.0.1:8000/`

## API Documentation

### Swagger UI
Access interactive API documentation at:
- Swagger: `http://127.0.0.1:8000/api/docs/`
- ReDoc: `http://127.0.0.1:8000/api/redoc/`

### Authentication Endpoints

```
POST   /api/auth/token/          - Login (get JWT tokens)
POST   /api/auth/token/refresh/  - Refresh access token
```

### User Endpoints

```
GET    /api/users/               - List users (admin only)
POST   /api/users/               - Create user (admin only)
GET    /api/users/{id}/          - Get user details
PATCH  /api/users/{id}/          - Update user
DELETE /api/users/{id}/          - Delete user (admin only)
GET    /api/users/me/            - Get current user profile
PATCH  /api/users/me/update/     - Update current user profile
POST   /api/users/me/change-password/ - Change password
GET    /api/users/{id}/roles/    - List user roles
POST   /api/users/{id}/assign-role/ - Assign role to user
DELETE /api/users/{id}/remove-role/{role_id}/ - Remove role
```

### Department Endpoints

```
GET    /api/departments/         - List departments
POST   /api/departments/         - Create department
GET    /api/departments/{id}/    - Get department details
PATCH  /api/departments/{id}/    - Update department
DELETE /api/departments/{id}/    - Delete department
GET    /api/departments/{id}/contacts/ - List contacts
POST   /api/departments/{id}/contacts/ - Add contact
DELETE /api/departments/{id}/contacts/{contact_id}/ - Delete contact
```

### RBAC Endpoints

```
GET    /api/rbac/roles/          - List roles
POST   /api/rbac/roles/          - Create role
GET    /api/rbac/roles/{id}/     - Get role details
POST   /api/rbac/roles/{id}/assign-permission/ - Assign permission
DELETE /api/rbac/roles/{id}/remove-permission/{perm_id}/ - Remove permission
GET    /api/rbac/permissions/    - List permissions
POST   /api/rbac/permissions/    - Create permission
```

### Item Endpoints

```
GET    /api/items/               - List items (with filters)
POST   /api/items/               - Create item
GET    /api/items/{id}/          - Get item details
PATCH  /api/items/{id}/          - Update item
DELETE /api/items/{id}/          - Delete item
PATCH  /api/items/{id}/verify/   - Verify item
GET    /api/items/{id}/attributes/ - List item attributes
POST   /api/items/{id}/attributes/ - Add attribute
PATCH  /api/items/{id}/attributes/{attr_id}/ - Update attribute
DELETE /api/items/{id}/attributes/{attr_id}/ - Delete attribute
```

### Catalogue Endpoints

```
GET    /api/catalogue/           - List item types
POST   /api/catalogue/           - Create item type
GET    /api/catalogue/{id}/      - Get item type details
PATCH  /api/catalogue/{id}/      - Update item type
DELETE /api/catalogue/{id}/      - Delete item type
```

### Location Endpoints

```
GET    /api/locations/districts/ - List districts
GET    /api/locations/mandals/?district_id={id} - List mandals
GET    /api/locations/villages/?mandal_id={id} - List villages
```

### Log Endpoints

```
GET    /api/logs/                - List activity logs
GET    /api/logs/{id}/           - Get log details
```

## RBAC Permission System

### Using the Permission Decorator

```python
from apps.rbac.permissions import has_permission

@has_permission("view_items")
def get(self, request):
    # Only users with 'view_items' permission can access
    ...
```

### Permission Checking Function

```python
from apps.rbac.permissions import check_user_permission

if check_user_permission(request.user, "create_items"):
    # User has permission
    ...
```

### Common Permissions

- `view_items` - View item list and details
- `create_items` - Create new items
- `update_items` - Update existing items
- `delete_items` - Delete items
- `verify_items` - Verify/approve items

## Data Models

### User Model
Custom user model with email-based authentication, department assignment, and verification status.

### Department Model
Organization units with multiple contact types (mobile, email, fax, telephone).

### Role & Permission Models
RBAC implementation with many-to-many relationships.

### Item Model
Physical assets with geolocation, status tracking, and dynamic attributes.

### Location Models
Three-tier geographic hierarchy: District > Mandal > Village.

### Log Model
Automatic activity tracking for all CRUD operations.

## Filtering & Search

All list endpoints support:
- **Filtering**: `?status=verified&dept=1`
- **Search**: `?search=laptop`
- **Ordering**: `?ordering=-created_at`
- **Pagination**: `?page=2&page_size=50`

## Example Usage

### 1. Login

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password123"}'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. Create Item

```bash
curl -X POST http://127.0.0.1:8000/api/items/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "iteminfo": 1,
    "dept": 1,
    "latitude": 17.385044,
    "longitude": 78.486671,
    "attributes": [
      {"key": "color", "value": "blue", "datatype": "string"},
      {"key": "serial_number", "value": "SN123456", "datatype": "string"}
    ]
  }'
```

### 3. List Items with Filters

```bash
curl -X GET "http://127.0.0.1:8000/api/items/?status=verified&dept=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Verify Item

```bash
curl -X PATCH http://127.0.0.1:8000/api/items/1/verify/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "verified",
    "operational_notes": "Item verified and operational"
  }'
```

## Admin Panel

Access Django admin at `http://127.0.0.1:8000/admin/`

Login with superuser credentials created during setup.

## Automatic Logging

All item operations are automatically logged:
- Item creation logs `created_by`
- Item updates/verification logs `verified_by`
- Logs include metadata (item name, department, status)

## Security Features

- JWT token-based authentication
- Password hashing with Django's built-in system
- RBAC with granular permissions
- CORS configuration for API access
- Admin-only endpoints protection
- User-specific data filtering

## Development

### Create Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Create Sample Data

```python
python manage.py shell

from apps.rbac.models import Permission, Role
from apps.departments.models import Department

# Create permissions
Permission.objects.create(name="view_items", description="Can view items")
Permission.objects.create(name="create_items", description="Can create items")
Permission.objects.create(name="verify_items", description="Can verify items")

# Create role
role = Role.objects.create(name="Manager", description="Department Manager")
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Generate strong `SECRET_KEY`
3. Configure `ALLOWED_HOSTS`
4. Set up proper PostgreSQL credentials
5. Collect static files: `python manage.py collectstatic`
6. Use production WSGI server (gunicorn, uWSGI)
7. Set up reverse proxy (nginx, Apache)
8. Configure HTTPS/SSL
9. Set up database backups

## Troubleshooting

### Database Connection Error
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists

### JWT Token Expired
- Request new token via `/api/auth/token/refresh/`
- Check token lifetime in settings

### Permission Denied
- Verify user has required role and permissions
- Check RBAC configuration

## License

This project is proprietary software for asset management.

## Support

For issues and questions, contact the development team.
