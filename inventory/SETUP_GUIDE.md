# Quick Setup Guide

## Step-by-Step Instructions

### 1. Install PostgreSQL
- Download and install PostgreSQL from https://www.postgresql.org/download/
- During installation, remember your postgres password

### 2. Create Database

Open PostgreSQL command line (psql) or pgAdmin and run:

```sql
CREATE DATABASE asset_management;
```

### 3. Setup Python Environment

```bash
# Navigate to project directory
cd inventory

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy environment template
# Windows:
copy .env.example .env
# Linux/Mac:
cp .env.example .env
```

Edit `.env` file and update:
- `SECRET_KEY` - Generate a random secret key
- `DB_PASSWORD` - Your PostgreSQL password
- Other settings as needed

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

Enter:
- Email: admin@example.com (or your preferred email)
- Name: Admin
- Password: (choose a strong password)

### 7. Load Initial RBAC Data

```bash
python manage.py shell < setup_initial_data.py
```

This will create:
- 15 permissions
- 4 roles (Admin, Manager, Field Officer, Viewer)
- Role-permission mappings

### 8. Run Development Server

```bash
python manage.py runserver
```

Visit:
- API: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- Swagger Docs: http://127.0.0.1:8000/api/docs/

## Quick Test

### 1. Login to get JWT token

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"admin@example.com\", \"password\": \"your_password\"}"
```

### 2. Use token to access API

```bash
curl -X GET http://127.0.0.1:8000/api/users/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Next Steps

1. Access admin panel at http://127.0.0.1:8000/admin/
2. Create sample departments
3. Create sample locations (Districts, Mandals, Villages)
4. Create item catalogue entries
5. Create test users and assign roles
6. Test API endpoints via Swagger UI

## Common Issues

### Port already in use
```bash
# Use different port
python manage.py runserver 8001
```

### Database connection error
- Check PostgreSQL is running
- Verify credentials in .env file
- Ensure database exists

### Permission errors
- Make sure to run `setup_initial_data.py`
- Assign roles to users in admin panel

## Production Checklist

Before deploying to production:

- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY`
- [ ] Update `ALLOWED_HOSTS`
- [ ] Configure proper database credentials
- [ ] Run `python manage.py collectstatic`
- [ ] Set up proper WSGI server (gunicorn)
- [ ] Configure reverse proxy (nginx)
- [ ] Set up SSL/HTTPS
- [ ] Configure database backups
- [ ] Set up logging and monitoring
