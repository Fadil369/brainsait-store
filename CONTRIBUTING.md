# Contributing to BrainSAIT Store

Welcome to the BrainSAIT Store project! We appreciate your interest in contributing to our B2B SaaS platform.

## 🛠️ Development Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 14+
- Redis 6+

### Quick Start
```bash
# Clone the repository
git clone https://github.com/Fadil369/brainsait-store.git
cd brainsait-store

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install

# Start development servers
npm run dev  # Frontend (http://localhost:3000)
cd ../backend && uvicorn app.main:app --reload  # Backend (http://localhost:8000)
```

## 📋 Coding Standards

### Python (Backend)
- Use `snake_case` for variables and functions
- Use `PascalCase` for classes
- Add type hints for all function parameters and return values
- Follow FastAPI patterns and conventions
- Maximum line length: 88 characters (Black formatter)
- Use docstrings for all public functions and classes

Example:
```python
from typing import Optional
from pydantic import BaseModel

class UserSchema(BaseModel):
    """User schema for API operations."""
    name: str
    email: str
    is_active: Optional[bool] = True

async def create_user(user_data: UserSchema) -> dict[str, Any]:
    """Create a new user in the system.
    
    Args:
        user_data: User information to create
        
    Returns:
        Created user data with ID
    """
    # Implementation here
    pass
```

### TypeScript (Frontend)
- Use `camelCase` for variables and functions
- Use `PascalCase` for components and types
- Always use TypeScript types/interfaces
- Use React functional components with hooks
- Follow Next.js 14 App Router patterns

Example:
```typescript
interface UserProps {
  id: string;
  name: string;
  isActive: boolean;
}

const UserCard: React.FC<UserProps> = ({ id, name, isActive }) => {
  const [loading, setLoading] = useState<boolean>(false);
  
  const handleUserAction = useCallback(async () => {
    setLoading(true);
    // Implementation here
    setLoading(false);
  }, []);

  return (
    <div className="user-card">
      {/* Component JSX */}
    </div>
  );
};
```

### CSS/Styling
- Use Tailwind CSS utility classes
- Follow mobile-first responsive design
- Support RTL (Right-to-Left) for Arabic
- Use semantic HTML5 elements

## 🔒 Security Guidelines

### Environment Variables
- Never commit `.env` files
- Use `.env.example` for template
- All secrets must be loaded from environment
- Use appropriate variable names (e.g., `DATABASE_URL`, `STRIPE_SECRET_KEY`)

### API Security
- Always validate input data with Pydantic
- Use proper authentication and authorization
- Implement rate limiting
- Follow OWASP security guidelines

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm run test          # Watch mode
npm run test:ci       # CI mode
npm run test:coverage # With coverage
```

### Test Requirements
- All new features must have tests
- Maintain >80% code coverage
- Use descriptive test names
- Test both success and error cases

## 📚 Documentation

### Code Documentation
- Add docstrings to all Python functions/classes
- Use JSDoc comments for TypeScript functions
- Keep comments up-to-date with code changes
- Document complex business logic

### API Documentation
- FastAPI automatically generates OpenAPI docs
- Access at `http://localhost:8000/docs`
- Add proper descriptions to all endpoints
- Include example requests/responses

## 🚀 Deployment

### Environment Configuration
- **Development**: Local development with mock data
- **Staging**: Full integration testing environment
- **Production**: Live environment at `store.brainsait.io`

### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: New features and improvements
- `hotfix/*`: Critical production fixes

## 📦 Dependencies

### Adding Dependencies
1. Check if dependency is necessary
2. Verify license compatibility
3. Check for security vulnerabilities
4. Update both `package.json`/`requirements.txt` and lock files

### Updating Dependencies
```bash
# Frontend
npm audit fix
npm update

# Backend
pip-audit
pip install --upgrade package-name
```

## 🔄 Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make Changes**
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation

3. **Test Locally**
   ```bash
   # Frontend
   npm run lint
   npm run build
   npm run test:ci
   
   # Backend
   pytest tests/
   python -m flake8 app/
   python -m mypy app/
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```
   
   Use conventional commit format:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation
   - `style:` Code style/formatting
   - `refactor:` Code refactoring
   - `test:` Adding tests
   - `chore:` Build/tooling changes

5. **Push and Create PR**
   ```bash
   git push origin feature/amazing-feature
   ```

## 📞 Support

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Email**: development@brainsait.com
- **Documentation**: Check README.md and inline code docs

## 📄 License

This project is proprietary software owned by BrainSAIT. All rights reserved.

---

Thank you for contributing to BrainSAIT Store! 🚀