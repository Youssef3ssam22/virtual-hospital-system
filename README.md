# Virtual Hospital Information System

Production-oriented hospital management backend built with Django and Django REST Framework. The platform is organized around an encounter-based architecture and covers hospital administration, laboratory workflows, billing and revenue cycle, authentication, audit logging, and supporting infrastructure.

## Project Snapshot

- Version: `2.0.0`
- API base path: `/api/v1/`
- Runtime: Docker + PostgreSQL
- Admin UI: Django Admin with Jazzmin customization
- Documentation: Swagger and ReDoc

## Core Capabilities

- Patient and encounter lifecycle management
- Administration portal for departments, wards, beds, catalogs, roles, permissions, and audit logs
- Laboratory Information System workflow with orders, specimens, results, critical values, and reports
- Billing and revenue cycle with patient accounts, invoices, payments, claims, denials, timelines, and immutable financial ledger
- Cross-module safeguards including idempotency, audit enforcement, state machines, and concurrency protection

## Main Modules

### Patients
- Patient registration and demographic records
- Encounter-centric workflow for outpatient, inpatient, and emergency visits
- Encounter lifecycle: `planned -> active -> completed -> cancelled`

### Administration
- Departments, wards, and beds
- Bed assignments and occupancy management
- Roles, permissions, and user-role mapping
- System settings and audit logs
- Lab, radiology, and service catalogs

### Laboratory
- Lab orders linked to patient encounters
- Specimen workflow with guarded status transitions
- Result verification and correction tracking
- Critical value escalation and report release flow

### Billing
- Patient accounts
- Invoices and line items
- Payments and claim lifecycle
- Financial timeline
- Immutable transaction ledger for charges, payments, and adjustments

## Production Safeguards Included

- Idempotency support for critical POST endpoints
- Audit logging for mutating operations and failed logins
- Scoped rate limiting for authentication and billing endpoints
- Row-level locking on sensitive workflows such as payments, result verification, and bed assignment
- Server-side financial calculations
- Encounter-based validation across lab and billing workflows
- Read-only financial ledger records after creation

## Technology Stack

- Python 3.11+
- Django 5
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- Django Channels
- drf-spectacular
- django-filter
- Jazzmin
- Neo4j
- Gunicorn
- Docker and Docker Compose

## Project Structure

```text
apps/
  admin/
  auth/
  billing/
  cdss/
  lab/
  patients/
  pharmacy/
  radiology/
config/
infrastructure/
shared/
templates/
tests/
```

The project follows a modular structure with domain, application, infrastructure, and interface layers across several apps.

## Quick Start With Docker

### 1. Clone the repository

```bash
git clone https://github.com/Youssef3ssam22/virtual-hospital-system.git
cd virtual-hospital-system
```

### 2. Create your environment file

```bash
copy .env.example .env
```

Update `.env` with your local settings if needed. Do not commit the real `.env` file.

### 3. Start the services

```bash
docker compose up --build
```

### 4. Run migrations if needed

```bash
docker exec vh_django-web-1 python manage.py migrate
```

### 5. Open the application

- Django Admin: `http://127.0.0.1:8000/admin/`
- Swagger Docs: `http://127.0.0.1:8000/api/docs/`
- ReDoc: `http://127.0.0.1:8000/api/redoc/`
- Health Check: `http://127.0.0.1:8000/health/`

## Local Development Without Docker

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create your environment file

```bash
copy .env.example .env
```

### 3. Apply migrations

```bash
python manage.py migrate
python manage.py check
```

### 4. Run the server

```bash
python manage.py runserver 0.0.0.0:8000
```

## Default Admin Access

If seed/setup has been run in the local environment, the default admin account is:

- Email: `admin@hospital.com`
- Password: `Admin@123!`

Change credentials for any shared or production-like environment.

## Example Operational Flow

### 1. Administration setup
- Create departments such as outpatient, inpatient, laboratory, and billing
- Create wards and beds
- Configure catalogs and permissions

### 2. Patient and encounter
- Register a patient
- Create an active encounter

### 3. Laboratory cycle
- Create a lab order
- Create and process a specimen
- Enter and verify results
- Finalize and release the report

### 4. Billing cycle
- Open a patient account
- Create an invoice linked to the encounter
- Add or auto-generate line items
- Process payment

## API and Documentation

- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- Health endpoint: `/health/`

All core APIs are exposed under:

```text
/api/v1/
```

## Testing and Verification

Useful commands:

```bash
python manage.py check
pytest -q
```

Useful project scripts:

- `verify_system.py`
- `run_system_test.py`
- `test_e2e_workflows.py`

## Supporting Documentation

The repository already includes detailed documentation files for setup, testing, workflows, and operational guidance, including:

- `START_HERE.md`
- `GETTING_STARTED.md`
- `SETUP.md`
- `QUICKSTART.md`
- `COMPLETE_GUIDE.md`
- `PROFESSIONAL_USER_GUIDE.md`
- `DOCUMENTATION_INDEX.md`

## Security Notes

- `.env` is excluded from version control
- Local SQLite files are excluded from version control
- The repository is prepared for PostgreSQL-based runtime
- Critical financial and laboratory workflows include transaction and validation safeguards

## License

This repository currently has no explicit license file. Add a license before public distribution if required by your project or university policy.
