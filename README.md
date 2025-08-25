# ALX Travel App - Backend

The ALX Travel App is a Django-based backend for a travel listing platform, designed with industry best practices for scalability, maintainability, and team collaboration.

## Project Overview

This project serves as the foundation for a travel platform, providing:

Robust API backend with Django REST Framework  
MySQL database configuration  
Automated API documentation with Swagger  
Secure environment management  
CORS support for cross-domain requests  
Future-ready task queuing with Celery/RabbitMQ  

## Features

RESTful API Architecture : Built with Django REST Framework  
Automated Documentation : Interactive Swagger UI at /swagger/  
Secure Configuration : Environment-based secrets management  
Cross-Origin Support : CORS headers for API accessibility  
MySQL Database : Production-ready database setup  
Task Queuing : Celery + RabbitMQ integration (future implementation)  

## Prerequisites

Python 3.12+  
Django 5.2.4+  
Django REST Framework  
MySQL 8.0+  
django-environ (for environment variables)  
RabbitMQ (for future Celery tasks)  
Git  

## Installation

1. Clone the repository  
git clone <https://github.com/your-username/alx_travel_app.git>  
cd alx_travel_app  
2. Create and activate virtual environment  
python -m venv venv  

### Linux/Mac

source venv/bin/activate

### Windows

venv\Scripts\activate  
3. Install dependencies  
pip install -r requirements.txt  
4. Configure environment variables  

Create a .env file in the project root:

SECRET_KEY='your-secret-key-here'
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

MYSQL_DATABASE=alx_travel_db
MYSQL_USER=alx_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_HOST=localhost
MYSQL_PORT=3306

### Chapa Payment Integration

CHAPA_SECRET_KEY=your_chapa_secret_key_here

## For future Celery tasks

CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//

5. Database setup
Create MySQL database and user:

CREATE DATABASE alx_travel_db;
CREATE USER 'alx_user'@'localhost' IDENTIFIED BY 'your_mysql_password';
GRANT ALL PRIVILEGES ON alx_travel_db.* TO 'alx_user'@'localhost';
FLUSH PRIVILEGES;

6. Run migrations
python manage.py migrate

### Running the Application

Start the development server:

python manage.py runserver
The application will be available at [http://localhost:8000](http://localhost:8000)

## Payment Integration (Chapa)

This project integrates Chapa for secure payment processing.

### Environment Variable

Add your Chapa secret key to your `.env` file:

CHAPA_SECRET_KEY=your_chapa_secret_key_here

### Payment API Usage

**Initiate Payment:**
POST `/api/payments/initiate/`
Body: `{ "booking_id": <booking_id>, "amount": <amount> }`
Returns a checkout URL for the user to complete payment.

**Verify Payment:**
GET `/api/payments/verify/?tx_ref=<transaction_id>`
Checks payment status and updates the Payment model accordingly.

**Note:** Use Chapa's sandbox environment for testing. See [Chapa Docs](https://developer.chapa.co/docs/) for more info.

## Project Structure

alx_travel_app/
├── .env.example                 # Environment variable template  
├── .gitignore                   # Git ignore rules  
├── manage.py                    # Django management script  
│
├── alx_travel_app/              # Main project package  
│   ├── __init__.py
│   ├── asgi.py
|   ├── requirement.txt          # Project dependencies  
│   ├── settings.py              # Project settings  
│   ├── urls.py                  # Main URL configuration  
│   ├── wsgi.py
|   └── listings/                # Listings application  
        ├── migrations/          # Database migrations  
        ├── __init__.py
        ├── admin.py             # Admin configuration  
        ├── apps.py              # App configuration  
        ├── models.py            # Database models  
        ├── tests.py             # Application tests  
        ├── urls.py              # App URL routes  
        └── views.py             # API views  
│   └── README.md

### Database Seeding

To populate the database with sample listings, bookings, and reviews:

### Run migrations

python manage.py makemigrations  
python manage.py migrate  
Seed the database:  
python manage.py seed  
This will create:  

10 sample listings  
1 test user ([test@example.com](mailto:test@example.com))  
Bookings for each listing  
Reviews for each listing  
Implementation Notes  
Models:  

Used proper field types and constraints (e.g., DecimalField for prices)  
Added related names for FK relationships  
Implemented choice fields with human-readable options  
Included automatic timestamps  
Serializers:  

Used ModelSerializers for automatic field mapping  
Protected read-only fields like timestamps  
Followed RESTful design principles  
Seeder:  

Handles data deletion before seeding  
Creates realistic sample data with variations  
Includes bookings and reviews for comprehensive seeding  
Provides console feedback during execution  
Uses proper date calculations for bookings  
Views:

Used ViewSets for comprehensive CRUD operations  
Added ordering by creation date for listings and bookings  
Implemented filtering for bookings by listing ID  
Used proper lookup fields for resource identification  
URLs:

DRF Router for automatic endpoint generation  
API mounted under /api/ namespace  
Maintained Swagger and ReDoc documentation paths  
Admin:

Comprehensive display configurations for each model  
Search and filtering capabilities  
Date hierarchy for bookings  
Custom ordering for all models  
Security:

Django admin requires authentication  
API endpoints follow RESTful security practices  
User permissions handled by Django's auth system  
The test user has a dummy password (should be changed in production)  
Sensitive fields are protected in serializers  
To use this implementation:

Create the files as specified  
Run migrations: python manage.py makemigrations && python manage.py migrate  
Create a superuser: python manage.py createsuperuser  
Start the server: python manage.py runserver  
Access:
API: [http://localhost:8000/api/listings/](http://localhost:8000/api/listings/)  
Admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)  
Docs: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)  
To use this app in production, implement JWT Authentication.  
API Documentation  
Access interactive API documentation:  

Swagger UI: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)  
ReDoc: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)  
API Endpoints  
Listings:

GET /api/listings/ - List all travel listings  
GET /api/listings/{id}/ - Get a specific listing  
POST /api/listings/ - Create a new listing  
PUT /api/listings/{id}/ - Update a listing
DELETE /api/listings/{id}/ - Delete a listing  
Bookings:

GET /api/bookings/ - List all bookings  
GET /api/bookings/{id}/ - Get a specific booking  
POST /api/bookings/ - Create a new booking  
PUT /api/bookings/{id}/ - Update a booking  
DELETE /api/bookings/{id}/ - Delete a booking  
Filter by listing: GET /api/bookings/?listing_id={id}  
Django Admin  
Access the admin interface at [http://localhost:8000/admin/](http://localhost:8000/admin/) to manage:

Listings  
Bookings  
Reviews  
Users  
Testing the API  
Start the development server:
python manage.py runserver

## Access API endpoints

Listings: [http://localhost:8000/api/listings/](http://localhost:8000/api/listings/)  
Bookings: [http://localhost:8000/api/bookings/](http://localhost:8000/api/bookings/)  
Use Swagger UI for interactive testing: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)  

## License

This project is for educational purpose within the ALX ProDEV program.