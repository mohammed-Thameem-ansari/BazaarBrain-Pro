# BazaarBrain-Pro Documentation

## Table of Contents

1. [Overview](#overview)
2. [Setup Instructions](#setup-instructions)
3. [Database Schema](#database-schema)
4. [API Reference](#api-reference)
5. [Authentication](#authentication)
6. [Agent Integration](#agent-integration)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

## Overview

BazaarBrain-Pro is an AI-powered business assistant for shopkeepers that combines:
- **Reality Capture Agent**: Dual LLM OCR processing (GPT Vision + Gemini Vision)
- **Simulation Agent**: Business "what-if" scenario analysis
- **FastAPI Backend**: RESTful API with Supabase database integration
- **JWT Authentication**: Secure user authentication and authorization

## Setup Instructions

### Prerequisites

- Python 3.8+
- Supabase account and project
- OpenAI API key
- Google Gemini API key

### 1. Environment Setup

Create a `.env` file in the root directory:

```bash
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Environment Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

### 2. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install required packages
pip install -r backend/requirements.txt
```

### 3. Database Setup

1. **Create Supabase Project**:
   - Go to [supabase.com](https://supabase.com)
   - Create new project
   - Note your Project URL and API keys

2. **Run Database Schema**:
   - Go to SQL Editor in Supabase dashboard
   - Copy and paste the contents of `docs/supabase_schema.sql`
   - Execute the script

3. **Verify Tables**:
   - Check that `users`, `transactions`, and `simulations` tables exist
   - Verify indexes and triggers are created

### 4. Start the Server

```bash
# From the backend directory
cd backend
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## Database Schema

### Tables

#### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    password TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Transactions Table
```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    raw_input TEXT NOT NULL,
    parsed_json JSONB NOT NULL,
    source TEXT NOT NULL DEFAULT 'image',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Simulations Table
```sql
CREATE TABLE simulations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    parameters JSONB NOT NULL,
    result JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Indexes
- `idx_transactions_user_id`: For fast user transaction lookups
- `idx_transactions_created_at`: For chronological ordering
- `idx_simulations_user_id`: For fast user simulation lookups
- `idx_users_email`: For fast email lookups

## API Reference

### Base URL
```
http://localhost:8000
```

### Authentication
All endpoints except `/health` require JWT authentication via Bearer token:

```bash
Authorization: Bearer <your_jwt_token>
```

### Endpoints

#### Health Checks

##### GET /
Root endpoint with API information.

**Response:**
```json
{
    "message": "Welcome to BazaarBrain-Pro API",
    "version": "1.0.0",
    "status": "running",
    "docs": "/docs",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

##### GET /health
Comprehensive health check including database status.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "services": {
        "api": "healthy",
        "database": "healthy"
    },
    "version": "1.0.0"
}
```

##### GET /api/v1/health
Basic health check endpoint.

##### GET /api/v1/health/detailed
Detailed health check with environment info.

##### GET /api/v1/health/ready
Readiness check for container orchestration.

##### GET /api/v1/health/live
Liveness check for container orchestration.

#### Receipt Processing

##### POST /api/v1/upload_receipt
Upload and process a receipt image.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/upload_receipt" \
  -H "Authorization: Bearer <token>" \
  -F "file=@receipt.jpg" \
  -F "source=receipt"
```

**Response:**
```json
{
    "success": true,
    "transaction_id": "uuid-here",
    "result": {
        "items": [
            {"name": "Coffee", "price": 3.50, "quantity": 1}
        ],
        "total": 3.50,
        "vendor": "Starbucks",
        "source": "gpt+gemini_agree"
    },
    "filename": "receipt.jpg",
    "processed_at": "2024-01-15T10:30:00Z"
}
```

##### GET /api/v1/transactions
Get user's transactions.

**Query Parameters:**
- `limit` (optional): Maximum number of transactions (default: 50, max: 100)

**Response:**
```json
{
    "success": true,
    "transactions": [...],
    "count": 5,
    "limit": 50,
    "user_id": "user-uuid"
}
```

##### GET /api/v1/transactions/{transaction_id}
Get specific transaction by ID.

##### DELETE /api/v1/transactions/{transaction_id}
Delete specific transaction.

##### GET /api/v1/stats
Get processing statistics.

#### Business Simulations

##### POST /api/v1/simulate
Run a business simulation.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/simulate" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"query": "What if I increase coffee price by 10%?"}'
```

**Response:**
```json
{
    "success": true,
    "simulation_id": "uuid-here",
    "query": "What if I increase coffee price by 10%?",
    "result": {
        "scenario": "increase_price",
        "item": "Coffee",
        "change": 10,
        "estimated_profit_change": 0.35
    },
    "processed_at": "2024-01-15T10:30:00Z"
}
```

##### GET /api/v1/simulations
Get user's simulations.

**Query Parameters:**
- `limit` (optional): Maximum number of simulations (default: 50, max: 100)

##### GET /api/v1/simulations/{simulation_id}
Get specific simulation by ID.

##### DELETE /api/v1/simulations/{simulation_id}
Delete specific simulation.

##### GET /api/v1/scenarios
Get available simulation scenarios and examples.

**Response:**
```json
{
    "success": true,
    "scenarios": {
        "price_increase": {
            "description": "Analyze the impact of increasing product prices",
            "examples": [
                "What if I increase coffee price by 10%?",
                "How would a 15% price hike affect my tea sales?"
            ]
        }
    }
}
```

##### GET /api/v1/stats
Get simulation statistics.

## Authentication

### JWT Token Structure

Supabase JWT tokens contain:
```json
{
    "sub": "user-uuid",
    "email": "user@example.com",
    "aud": "authenticated",
    "exp": 1234567890,
    "iat": 1234567890
}
```

### Token Verification

The API verifies tokens using:
- **Algorithm**: HS256
- **Audience**: "authenticated"
- **Secret**: Supabase JWT secret

### Protected Endpoints

All endpoints except `/health` require authentication:
- `/api/v1/upload_receipt`
- `/api/v1/transactions`
- `/api/v1/simulate`
- `/api/v1/simulations`

## Agent Integration

### Reality Capture Agent

The Reality Capture Agent automatically saves OCR results to the database:

```python
from agents.reality_capture_agent import RealityCaptureAgent

agent = RealityCaptureAgent()
result = agent.process_receipt(
    image_path="receipt.jpg",
    user_id="user-uuid",
    save_to_db=True  # Default: True
)
```

**Database Integration:**
- Automatically calls `db.save_transaction()`
- Stores parsed JSON results
- Links to user account
- Tracks processing source

### Simulation Agent

The Simulation Agent automatically saves simulation results:

```python
from agents.simulation_agent import SimulationAgent

agent = SimulationAgent()
result = agent.simulate(
    query="What if I increase coffee price by 10%?",
    user_id="user-uuid",
    save_to_db=True  # Default: True
)
```

**Database Integration:**
- Automatically calls `db.save_simulation()`
- Stores query, parameters, and results
- Links to user account
- Tracks simulation metadata

## Testing

### Run All Tests

```bash
# From the root directory
python -m pytest tests/

# Or run specific test files
python -m pytest tests/test_backend.py
python -m pytest tests/test_reality_capture.py
python -m pytest tests/test_simulation_agent.py
```

### Test Coverage

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run -m pytest tests/
coverage report
coverage html  # Generate HTML report
```

### Test Categories

1. **Unit Tests**: Individual function testing
2. **Integration Tests**: API endpoint testing
3. **Database Tests**: Database operation testing
4. **Authentication Tests**: JWT verification testing
5. **Agent Tests**: AI agent functionality testing

## Deployment

### Production Considerations

1. **Environment Variables**:
   - Set `ENVIRONMENT=production`
   - Set `DEBUG=false`
   - Use strong, unique API keys

2. **Security**:
   - Configure CORS properly
   - Use HTTPS
   - Implement rate limiting
   - Set secure JWT secrets

3. **Database**:
   - Use production Supabase instance
   - Enable Row Level Security (RLS)
   - Configure proper backups

4. **Monitoring**:
   - Enable logging
   - Set up health checks
   - Monitor API performance

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment-Specific Configs

```bash
# Development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Staging
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# Production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

**Symptoms:**
- Health check shows database as unhealthy
- API endpoints return 500 errors

**Solutions:**
- Verify Supabase URL and API keys
- Check network connectivity
- Verify database tables exist
- Check Supabase project status

#### 2. Authentication Errors

**Symptoms:**
- 401 Unauthorized errors
- JWT verification failures

**Solutions:**
- Verify JWT token format
- Check token expiration
- Verify Supabase JWT secret
- Check token audience

#### 3. Agent Processing Failures

**Symptoms:**
- OCR processing errors
- Simulation failures

**Solutions:**
- Verify OpenAI and Gemini API keys
- Check API rate limits
- Verify prompt files exist
- Check image format compatibility

#### 4. File Upload Issues

**Symptoms:**
- File upload failures
- Processing errors

**Solutions:**
- Verify file format (JPEG, PNG)
- Check file size limits
- Verify file permissions
- Check disk space

### Debug Mode

Enable debug mode for detailed error information:

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

### Logs

Check application logs for detailed error information:

```bash
# Application logs
tail -f logs/app.log

# Error logs
tail -f logs/error.log
```

### Support

For additional support:
1. Check the [GitHub Issues](https://github.com/your-repo/issues)
2. Review the [Supabase Documentation](https://supabase.com/docs)
3. Check [FastAPI Documentation](https://fastapi.tiangolo.com/)

## API Examples

### Complete Workflow Example

1. **Authenticate User**:
```bash
# Get JWT token from Supabase Auth
curl -X POST "https://your-project.supabase.co/auth/v1/token?grant_type=password" \
  -H "apikey: your_anon_key" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'
```

2. **Upload Receipt**:
```bash
curl -X POST "http://localhost:8000/api/v1/upload_receipt" \
  -H "Authorization: Bearer <jwt_token>" \
  -F "file=@receipt.jpg" \
  -F "source=receipt"
```

3. **Run Simulation**:
```bash
curl -X POST "http://localhost:8000/api/v1/simulate" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"query":"What if I increase coffee price by 10%?"}'
```

4. **Get Results**:
```bash
# Get transactions
curl -H "Authorization: Bearer <jwt_token>" \
  "http://localhost:8000/api/v1/transactions"

# Get simulations
curl -H "Authorization: Bearer <jwt_token>" \
  "http://localhost:8000/api/v1/simulations"
```

### Error Response Format

```json
{
    "detail": "Error message description",
    "status_code": 400,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Success Response Format

```json
{
    "success": true,
    "data": {...},
    "message": "Operation completed successfully",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

---

**Last Updated**: January 2024  
**Version**: 1.0.0  
**Maintainer**: BazaarBrain Team
