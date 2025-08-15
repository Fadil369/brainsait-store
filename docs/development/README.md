# Development Guide - BrainSAIT Store

## Prerequisites

### System Requirements
- **Node.js**: 18.0.0 or higher
- **Python**: 3.11 or higher
- **Git**: Latest version
- **Docker**: (Optional) For database setup

### Required Accounts
- **Cloudflare Account**: For deployment
- **GitHub Account**: For version control
- **PostgreSQL Database**: Production database

## Development Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/Fadil369/brainsait-store.git
cd brainsait-store
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations (when available)
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev
```

### 4. Database Setup

#### Option A: Docker (Recommended for Development)
```bash
# Create docker-compose.yml for local development
cat > docker-compose.dev.yml << EOF
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: brainsait_store
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
EOF

# Start services
docker-compose -f docker-compose.dev.yml up -d
```

#### Option B: Local Installation
Follow PostgreSQL and Redis installation guides for your operating system.

## Environment Configuration

### Backend Environment Variables
```bash
# Application
APP_NAME="BrainSAIT Store API"
APP_VERSION="1.0.0"
ENVIRONMENT="development"
DEBUG=true

# Database
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/brainsait_store"
REDIS_URL="redis://localhost:6379"

# Security
SECRET_KEY="your-secret-key-here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Services
STRIPE_SECRET_KEY="sk_test_..."
PAYPAL_CLIENT_ID="your-paypal-client-id"
```

### Frontend Environment Variables
```bash
# API Configuration
NEXT_PUBLIC_API_URL="http://localhost:8000"
NEXT_PUBLIC_ENVIRONMENT="development"

# Payment Configuration
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_test_..."
NEXT_PUBLIC_PAYPAL_CLIENT_ID="your-paypal-client-id"

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_PAYMENTS=true
```

## Development Workflow

### 1. Branch Management
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push to remote
git push origin feature/your-feature-name

# Create pull request on GitHub
```

### 2. Code Formatting and Linting

#### Backend (Python)
```bash
# Format code with Black
black app/

# Sort imports with isort
isort app/

# Lint with flake8
flake8 app/

# Type checking with mypy
mypy app/
```

#### Frontend (TypeScript/React)
```bash
# Format with Prettier
npm run format

# Lint with ESLint
npm run lint

# Type checking
npm run type-check
```

### 3. Testing

#### Backend Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_specific.py

# Run tests with verbose output
pytest -v
```

#### Frontend Tests
```bash
# Run all tests
npm test

# Run tests in CI mode
npm run test:ci

# Run tests with coverage
npm run test:coverage
```

## API Development

### Adding New Endpoints

1. **Create the API route** in `backend/app/api/v1/`
```python
from fastapi import APIRouter, Depends
from app.core.auth import get_current_user

router = APIRouter()

@router.get("/example")
async def get_example(current_user = Depends(get_current_user)):
    """
    Get example data
    
    Returns example data for the current user.
    """
    return {"message": "Example response"}
```

2. **Add Pydantic models** in `backend/app/schemas/`
```python
from pydantic import BaseModel

class ExampleResponse(BaseModel):
    message: str
    data: dict = {}
```

3. **Register the router** in `backend/app/main.py`
```python
from app.api.v1 import example

app.include_router(
    example.router,
    prefix="/api/v1/example",
    tags=["example"]
)
```

### Database Models

1. **Create SQLAlchemy model** in `backend/app/models/`
```python
from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base

class Example(Base):
    __tablename__ = "examples"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

2. **Create migration** (when Alembic is set up)
```bash
alembic revision --autogenerate -m "Add example table"
alembic upgrade head
```

## Frontend Development

### Component Structure
```
src/
├── components/           # Reusable components
│   ├── ui/              # Basic UI components
│   ├── forms/           # Form components
│   └── layout/          # Layout components
├── pages/               # Next.js pages
├── hooks/               # Custom React hooks
├── lib/                 # Utility functions
├── styles/              # Global styles
└── types/               # TypeScript type definitions
```

### Creating New Components
```typescript
// src/components/Example.tsx
import { FC } from 'react';

interface ExampleProps {
  title: string;
  description?: string;
}

export const Example: FC<ExampleProps> = ({ title, description }) => {
  return (
    <div className="p-4 border rounded">
      <h2 className="text-xl font-bold">{title}</h2>
      {description && <p className="text-gray-600">{description}</p>}
    </div>
  );
};
```

### API Integration
```typescript
// src/lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

## Debugging

### Backend Debugging
```python
# Add debug logging
import logging
logger = logging.getLogger(__name__)

@router.get("/debug")
async def debug_endpoint():
    logger.info("Debug endpoint called")
    logger.debug("Detailed debug information")
    return {"debug": True}
```

### Frontend Debugging
```typescript
// Use React Developer Tools
// Add console.log for debugging
console.log('Component props:', props);

// Use debugger statement
debugger;
```

## Performance Optimization

### Backend Performance
- **Database Queries**: Use async/await and connection pooling
- **Caching**: Implement Redis caching for frequent queries
- **Response Compression**: Enable gzip compression
- **Monitoring**: Use Prometheus metrics

### Frontend Performance
- **Code Splitting**: Use dynamic imports
- **Image Optimization**: Use Next.js Image component
- **Bundle Analysis**: Run `npm run analyze`
- **Caching**: Implement proper caching strategies

## Common Issues and Solutions

### Backend Issues

#### Database Connection Error
```bash
# Check database is running
docker-compose -f docker-compose.dev.yml ps

# Check connection string
echo $DATABASE_URL
```

#### Import Errors
```bash
# Check Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}"

# Ensure virtual environment is activated
which python
```

### Frontend Issues

#### Node Modules Issues
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### TypeScript Errors
```bash
# Check types
npm run type-check

# Clear Next.js cache
rm -rf .next
npm run dev
```

## Contribution Guidelines

### Code Style
- **Python**: Follow PEP 8, use Black for formatting
- **TypeScript**: Use Prettier and ESLint configuration
- **Commit Messages**: Use conventional commit format

### Pull Request Process
1. Create feature branch from main
2. Make minimal, focused changes
3. Add tests for new functionality
4. Update documentation if needed
5. Ensure all tests pass
6. Request review from team members

### Documentation
- Update README.md for user-facing changes
- Add inline comments for complex logic
- Update API documentation for new endpoints
- Include examples in documentation

## Next Steps

- [API Documentation](../api/README.md)
- [Deployment Guide](../deployment/README.md)
- [Testing Strategy](./testing.md)
- [Security Guidelines](./security.md)