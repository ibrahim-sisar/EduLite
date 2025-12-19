# EduLite Coding Standards

## General Principles
- **Simplicity over complexity** - This is a volunteer project, code should be approachable
- **Documentation** - Comment complex logic, especially for newcomers
- **Testing** - Write tests for new features and bug fixes
- **Type safety** - Use type hints in Python, TypeScript in frontend

## Python/Django Backend Standards

### Code Formatting
- **Black** formatter with 88 character line length
- Configuration in `pyproject.toml`
- Automatically run via pre-commit hooks
- Target Python versions: 3.8-3.12

### Type Checking
- **mypy** for static type analysis
- Warning-only, non-blocking in CI
- Type hints encouraged but not strictly enforced
- Many Django-specific modules have `ignore_errors = true` due to false positives

### Naming Conventions
- **Models**: PascalCase (e.g., `UserProfile`, `CourseMembership`)
- **Functions/methods**: snake_case (e.g., `get_user_friends_ids`, `can_be_found_by_user`)
- **Variables**: snake_case
- **Constants**: UPPER_SNAKE_CASE (e.g., `SEARCH_VISIBILITY_CHOICES`)
- **Class Meta**: Use `verbose_name` and `verbose_name_plural` for admin
- **Related names**: Descriptive, e.g., `related_name="course_memberships"`

### Django App Structure
Each app follows this pattern:
```
app_name/
├── migrations/
├── tests/              # Organized into subdirectories
│   ├── models/
│   ├── views/
│   ├── serializers/
│   └── ...
├── logic/              # Business logic separate from views (optional)
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── serializers.py
├── views.py
├── urls.py
├── permissions.py      # Custom permissions
├── signals.py          # Django signals
└── pagination.py       # Custom pagination (optional)
```

### Models
- Always include `__str__` method for admin readability
- Use `clean()` for model-level validation
- Add `help_text` to fields for documentation
- Use `related_name` on ForeignKey/ManyToMany fields
- Add database indexes for frequently queried fields
- Use choices from separate `model_choices.py` or `models_choices.py`

Example:
```python
class CourseMembership(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="course_memberships",
        help_text="The user who is a member of the course.",
    )
    
    def clean(self) -> None:
        super().clean()
        # Validation logic here
        
    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.role}"
```

### Serializers
- Use `read_only_fields` in Meta class
- Provide custom validation in `validate()` and `validate_<field>()`
- Add field-level help text via `help_text` in serializer fields
- Override `to_representation()` for custom output formatting

### Views
- Use DRF generic views and viewsets
- Use `@extend_schema` from drf-spectacular for API documentation
- Implement permission checks with DRF permission classes
- Use `@transaction.atomic` for multi-step database operations
- Log important actions with Python's logging module

Example:
```python
class CourseCreateView(generics.CreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Create a course",
        description="...",
        tags=["Courses"],
    )
    def post(self, request, *args, **kwargs):
        logger.debug("Course creation requested by user %s", request.user)
        return super().post(request, *args, **kwargs)
```

### Testing
- Test files use `test_*.py` naming convention
- Organize tests by component (models, views, serializers, etc.)
- Use Django's `TestCase` or `APITestCase` from DRF
- Use `setUp()` for test data creation
- Test both success and failure cases
- Use descriptive test method names: `test_<what>_<condition>_<expected>`

Example test structure:
```
users/tests/
├── models/
│   ├── test_user_profile.py
│   └── test_user_profile_privacy_settings.py
├── views/
│   ├── test_UserRegistrationView.py
│   └── test_SendFriendRequestView.py
└── serializers/
    └── test_UserSerializer.py
```

### Permissions
- Create custom permission classes in `permissions.py`
- Inherit from `BasePermission`
- Implement `has_permission()` and/or `has_object_permission()`

### Validation
- Use `ValidationError` from `django.core.exceptions` in models
- Use serializer validation in `validate()` methods
- Provide clear, user-friendly error messages

## Frontend (React/TypeScript) Standards

### File Organization
- **Components**: PascalCase (e.g., `Button.tsx`, `Navbar.tsx`)
- **Pages**: PascalCase with "Page" suffix (e.g., `LoginPage.tsx`)
- **Services**: camelCase (e.g., `api.ts`, `profileApi.ts`)
- **Types**: camelCase with `.types.ts` suffix (e.g., `auth.types.ts`)
- **Hooks**: camelCase with `use` prefix (e.g., `useAuth.ts`)
- **Contexts**: PascalCase with "Context" suffix (e.g., `AuthContext.tsx`)

### TypeScript
- **Strict mode enabled** - full type safety
- Define interfaces for all props and data structures
- Export interfaces from `.types.ts` files
- Use proper typing for API responses

Example:
```typescript
export interface LoginFormData {
  username: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
}
```

### Components
- Functional components with TypeScript
- Use `.tsx` extension for components with JSX
- Use `.ts` extension for utilities and types
- Props should be typed with interfaces
- Use descriptive prop names

### Migration to TypeScript
- Project is **gradually migrating** from JavaScript to TypeScript
- New components should be written in TypeScript
- Common components (`Button.tsx`, `Input.tsx`) already migrated
- Legacy components are `.jsx` files (to be migrated)

### Styling
- **Tailwind CSS v4** - utility-first approach
- Use Tailwind classes, avoid custom CSS when possible
- Component-specific styles in separate CSS files if needed
- Support for dark mode via Tailwind

### i18n (Internationalization)
- Use `react-i18next` for translations
- Store translations in `src/i18n/locales/`
- Support for Arabic (`ar`) and English (`en`)
- Wrap user-facing strings with `t()` function

## Git Commit Standards

### Commit Message Format
```
<type>: <subject>

<optional body>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat: add slideshow model with course relationship
fix: resolve friend request duplicate validation error
docs: update API endpoint documentation for courses
test: add unit tests for slideshow serializer
```

## Pre-commit Hooks

The following checks run automatically on commit:
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON validation
- Large file check (max 1MB)
- Merge conflict detection
- Python syntax validation
- **Black** formatting (auto-fix)
- **mypy** type checking (manual stage only)

## Documentation Standards

### Code Comments
- Explain **why**, not **what** the code does
- Use docstrings for functions, classes, and modules
- Document complex business logic
- Add inline comments for non-obvious code

### Docstring Format
```python
def can_be_found_by_user(self, requesting_user: "AbstractUser") -> bool:
    """
    Check if this user profile can be found in search by the requesting user.
    
    Args:
        requesting_user: The user performing the search
        
    Returns:
        bool: True if the profile should appear in search results
    """
```

### API Documentation
- Use `@extend_schema` decorator for all API endpoints
- Include summary, description, tags
- Provide request/response examples
- Document error responses

## Performance Considerations

### Database
- Use `select_related()` for forward ForeignKey relationships
- Use `prefetch_related()` for reverse relationships and ManyToMany
- Use `.exists()` instead of counting or fetching
- Add database indexes to frequently queried fields
- Avoid N+1 queries

Example:
```python
# Bad - N+1 query
if self.user_profile.friends.count() > 0:

# Good - exists() is more efficient
if self.user_profile.friends.exists():
```

### Optimization
- Use pagination for list endpoints
- Cache static choice data
- Minimize WebSocket message size
- Consider offline-first patterns for low-connectivity scenarios

## Security

### Authentication
- JWT tokens for API authentication
- Token refresh mechanism
- Secure password hashing (Django default)

### Permissions
- Always use permission classes on views
- Validate user ownership for updates/deletes
- Check privacy settings before exposing data
- Use `@transaction.atomic` for data consistency

### Validation
- Always validate user input
- Use Django/DRF validation mechanisms
- Sanitize file uploads
- Check file size limits
