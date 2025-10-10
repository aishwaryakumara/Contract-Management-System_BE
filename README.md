# Contract Management System - Backend

## Overview

Contract Management System - web application designed to manage contract lifecycles, including creation, document storage, renewal, and automated data extraction using Natural Language Processing. 

## Technology Stack

### Backend Framework
- Python 3.13
- Flask 3.1.2
- Flask-SQLAlchemy 3.1.1 (ORM)
- Flask-Migrate 4.1.0 (Database Migrations)
- Flask-JWT-Extended 4.7.1 (Authentication)
- Flask-CORS 6.0.1 (Cross-Origin Resource Sharing)

### Database
- PostgreSQL 14+
- Alembic 1.16.5 (Migration Management)

### Natural Language Processing
- spaCy 3.8.7
- en_core_web_sm (English language model)
- python-docx 1.2.0 (Document parsing)

### Additional Libraries
- python-dotenv 1.1.1 (Environment configuration)
- python-json-logger 4.0.0 (Structured logging)
- Werkzeug 3.1.3 (Security utilities)
- pytest 8.4.2 (Testing framework)

## Features

### Core Functionality
- Contract creation and management
- Multi-version contract support
- Document upload and storage (PDF, DOC, DOCX)
- Contract renewal workflow
- Advanced search and filtering
- Activity history tracking

### NLP-Powered Features
- Automated contract data extraction
- Named Entity Recognition (NER) for:
  - Client names and organizations
  - Contract dates (start, end, renewal)
  - Contract values and amounts
  - Contact information

### Security
- JWT-based authentication
- Password hashing with Werkzeug
- Role-based access control ( Future )
- Secure file upload validation

### Audit & Compliance
- Comprehensive activity logging
- Audit trail for all contract modifications
- User action tracking
- Timestamp tracking for all entities

## Prerequisites

- Python 3.13 or higher
- PostgreSQL 14 or higher
- pip (Python package manager)
- Virtual environment tool (venv)

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd contract_management_system_backend
```

### 2. Create Virtual Environment

```bash
python3 -m venv nbs_cms_venv
source nbs_cms_venv/bin/activate  # On Windows: nbs_cms_venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install Flask-Migrate python-docx python-json-logger spacy
```

### 4. Install spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

## Database Setup

### 1. Create PostgreSQL Database

```bash
psql -U postgres
CREATE DATABASE nbs_contract_management;
CREATE USER contract_admin WITH PASSWORD 'xxxxxxx';
GRANT ALL PRIVILEGES ON DATABASE nbs_contract_management TO contract_admin;
\q
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Flask Configuration
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://contract_admin:xxxxxxxx@localhost:5432/nbs_contract_management

# File Upload Configuration
UPLOAD_FOLDER=./storage/contracts
MAX_FILE_SIZE_MB=10
ALLOWED_EXTENSIONS=pdf,doc,docx

# CORS Configuration
CORS_ORIGINS=http://localhost:3000

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

### 3. Initialize Database

```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### 4. Seed Database (Optional)

```bash
python seed_database.py
```

This creates:
- Default contract types (Service, NDA, Employment, Vendor, Lease)
- Default contract statuses (Draft, Active, Expired, Terminated, Renewed)
- Default document types (Main Contract, Amendment, Supporting Document)
- Test user accounts

## Running the Application

### Development Server

```bash
python run.py
```

The application will be available at `http://localhost:5000`

### Production Server

For production deployment, use a WSGI server such as Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## API Endpoints

### Authentication
- POST `/api/auth/login` - User login
- GET `/api/auth/me` - Get current user information

### Contracts
- GET `/api/contracts` - List all contracts
- GET `/api/contracts/{id}` - Get contract details
- POST `/api/contracts` - Create new contract
- PUT `/api/contracts/{id}` - Update contract
- POST `/api/contracts/{id}/renew` - Renew contract
- POST `/api/contracts/extract` - Extract data from contract document
- GET `/api/contracts/{id}/history` - Get contract activity history

### Documents
- POST `/api/contracts/{id}/documents` - Upload supporting document
- GET `/api/documents/{id}/download` - Download document
- DELETE `/api/documents/{id}` - Delete document

### Lookups
- GET `/api/contract-types` - Get contract types
- GET `/api/contract-status` - Get contract statuses

## Project Structure

```
contract_management_system_backend/
├── app/
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration settings
│   ├── extensions.py            # Flask extensions
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── contracts.py     # Contract endpoints
│   │       └── documents.py     # Document endpoints
│   ├── models/
│   │   ├── base.py             # Base models and mixins
│   │   ├── user.py             # User model
│   │   ├── contract.py         # Contract model
│   │   ├── document.py         # Document model
│   │   ├── activity_history.py # Activity tracking
│   │   └── audit_log.py        # Audit logging
│   ├── repositories/           # Data access layer
│   ├── services/               # Business logic layer
│   │   ├── contract_service.py
│   │   ├── storage_service.py
│   │   └── ner_service.py
│   └── utils/                  # Utility functions
├── migrations/                 # Database migrations
├── storage/                    # File storage
│   └── contracts/
├── logs/                       # Application logs
├── tests/                      # Unit and integration tests
├── requirements.txt            # Python dependencies
├── run.py                      # Application entry point
├── seed_database.py           # Database seeding script
└── .env                       # Environment variables
```

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| FLASK_ENV | Application environment | development |
| SECRET_KEY | Flask secret key | - |
| JWT_SECRET_KEY | JWT signing key | - |
| DATABASE_URL | PostgreSQL connection string | - |
| UPLOAD_FOLDER | File storage directory | ./storage/contracts |
| MAX_FILE_SIZE_MB | Maximum upload size in MB | 10 |
| ALLOWED_EXTENSIONS | Allowed file extensions | pdf,doc,docx |
| CORS_ORIGINS | Allowed CORS origins | http://localhost:3000 |
| LOG_LEVEL | Logging level | INFO |
| LOG_FILE | Log file path | ./logs/app.log |

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=app tests/
```

### Run Specific Test File

```bash
pytest tests/unit/test_models/test_contract.py
```

## Database Migrations

### Create New Migration

```bash
flask db migrate -m "Description of changes"
```

### Apply Migrations

```bash
flask db upgrade
```

### Rollback Migration

```bash
flask db downgrade
```

### View Migration History

```bash
flask db history
```

## Development Guidelines

### Code Structure
- Follow repository pattern for data access
- Use service layer for business logic
- Keep controllers thin (API endpoints)
- Implement error handling at all layers

### Database Operations
- Always use migrations for schema changes
- Never modify database directly in production
- Test migrations before applying

### Security Best Practices
- Never commit `.env` file
- Use environment variables for sensitive data
- Validate all user inputs
- Sanitize file uploads
- Use parameterized queries (SQLAlchemy ORM handles this)

## Troubleshooting

### Database Connection Issues

```bash
# Verify PostgreSQL is running
pg_isready

# Check database exists
psql -U contract_admin -d nbs_contract_management -c "\dt"
```

### Migration Errors

```bash
# Reset migrations (development only)
flask db downgrade base
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### File Upload Issues

```bash
# Verify storage directory exists and is writable
ls -la storage/contracts/
chmod 755 storage/contracts/
```

## Support and Documentation

For additional information:
- Review API endpoint documentation in respective controller files
- Check model definitions in `app/models/`
- Refer to service layer for business logic implementation
- Consult Flask documentation: https://flask.palletsprojects.com/

## License

Proprietary - All Rights Reserved
