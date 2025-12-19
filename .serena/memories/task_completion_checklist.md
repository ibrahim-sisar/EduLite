# Task Completion Checklist

When completing a task in EduLite, follow this checklist to ensure quality and consistency:

## Before Starting
- [ ] Read the task requirements carefully
- [ ] Check if there are related open issues or PRs
- [ ] Create a feature branch with descriptive name (e.g., `feature/slideshow-app`)
- [ ] Understand the existing code patterns in the relevant app

## During Development

### Code Quality
- [ ] Follow naming conventions (snake_case for functions, PascalCase for classes)
- [ ] Add type hints to Python functions
- [ ] Use TypeScript for new React components
- [ ] Write clear, descriptive variable and function names
- [ ] Add comments for complex logic
- [ ] Keep functions focused and small (single responsibility)

### Django Backend
- [ ] Add `__str__` methods to models
- [ ] Include `help_text` on model fields
- [ ] Use `related_name` on relationships
- [ ] Implement `clean()` for model validation
- [ ] Create serializers for models
- [ ] Use DRF generic views or viewsets
- [ ] Add `@extend_schema` decorators for API documentation
- [ ] Implement appropriate permission classes
- [ ] Add database indexes for frequently queried fields
- [ ] Use `select_related()`/`prefetch_related()` to avoid N+1 queries

### Frontend
- [ ] Create TypeScript interfaces for props and data
- [ ] Use functional components with hooks
- [ ] Follow Tailwind CSS conventions
- [ ] Support dark mode if applicable
- [ ] Add i18n translations for user-facing strings
- [ ] Handle loading and error states
- [ ] Make components responsive

### Testing
- [ ] Write unit tests for models
- [ ] Write tests for serializers
- [ ] Write integration tests for views/API endpoints
- [ ] Test success cases
- [ ] Test failure/edge cases
- [ ] Test permission checks
- [ ] Run tests locally before committing
- [ ] Ensure all tests pass

## Before Committing

### Run Quality Checks
```bash
# Backend checks
cd backend/EduLite
python manage.py test                    # Run tests
python manage.py check                   # Check Django configuration
black backend/                          # Format code (from project root)

# Frontend checks
cd Frontend/EduLiteFrontend
npm run type-check                      # Check TypeScript
npm run lint                            # Run ESLint
npm test                                # Run frontend tests
```

### Pre-commit
- [ ] Pre-commit hooks run automatically and pass
- [ ] No trailing whitespace
- [ ] Files end with newline
- [ ] No large files committed
- [ ] Black formatting applied
- [ ] YAML/JSON files are valid

### Git
- [ ] Stage relevant files only (`git add <files>`)
- [ ] Write descriptive commit message following convention:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation
  - `test:` for tests
  - `refactor:` for code refactoring
- [ ] Commit message is clear and explains **why** (not just what)

## After Committing

### Before Opening PR
- [ ] Push branch to GitHub
- [ ] Pull latest main and resolve any conflicts
- [ ] Run tests again after merge
- [ ] Check that migrations are included (if model changes)

### Pull Request
- [ ] Create PR with descriptive title
- [ ] Fill out PR template (if exists)
- [ ] Link related issues
- [ ] Add screenshots for UI changes
- [ ] Request review from maintainers
- [ ] Respond to review comments promptly
- [ ] Update PR based on feedback

## Backend-Specific Checklist

### When Adding New Models
- [ ] Create migration file
- [ ] Register in admin.py with proper display fields
- [ ] Add to API with serializer and views
- [ ] Create URL patterns
- [ ] Document in API docs
- [ ] Add choices to `model_choices.py` if needed

### When Adding New API Endpoints
- [ ] Add to urls.py
- [ ] Create view with appropriate permissions
- [ ] Add OpenAPI documentation with `@extend_schema`
- [ ] Create or update serializer
- [ ] Write API tests
- [ ] Document in `Documentation/API-Endpoints/`

### When Modifying Models
- [ ] Create migration: `python manage.py makemigrations`
- [ ] Review generated migration
- [ ] Run migration locally: `python manage.py migrate`
- [ ] Update serializers if needed
- [ ] Update tests
- [ ] Commit migration files with changes

## Frontend-Specific Checklist

### When Adding New Pages
- [ ] Create page component in `src/pages/`
- [ ] Add route in App.jsx/App.tsx
- [ ] Add to navigation if needed
- [ ] Add i18n translations
- [ ] Test routing

### When Adding New Components
- [ ] Use TypeScript (.tsx extension)
- [ ] Create in appropriate directory (common, pages, etc.)
- [ ] Define prop interfaces
- [ ] Add to exports if reusable
- [ ] Write component tests

### When Calling APIs
- [ ] Create service functions in `src/services/`
- [ ] Type API responses
- [ ] Handle errors gracefully
- [ ] Show loading states
- [ ] Use auth tokens from context

## Documentation
- [ ] Update README if needed
- [ ] Add/update API endpoint documentation
- [ ] Update CONTRIBUTING.md if process changes
- [ ] Add code comments for complex logic
- [ ] Document new environment variables

## Performance
- [ ] Check for N+1 queries (use Django Debug Toolbar locally)
- [ ] Add database indexes where appropriate
- [ ] Use pagination for large datasets
- [ ] Optimize large imports/exports
- [ ] Consider caching for expensive operations

## Security
- [ ] Validate all user input
- [ ] Check permissions on all views
- [ ] Don't expose sensitive data in API responses
- [ ] Use HTTPS in production
- [ ] Check file upload size limits
- [ ] Sanitize file uploads

## Deployment Considerations
- [ ] Check for new dependencies in requirements.txt or package.json
- [ ] Update environment variable documentation
- [ ] Test with production-like settings locally
- [ ] Consider migration strategy for database changes
- [ ] Check Redis/WebSocket functionality if changed

## Final Check
- [ ] Code works locally
- [ ] All tests pass
- [ ] No console errors/warnings
- [ ] Code follows project standards
- [ ] Documentation is updated
- [ ] PR is ready for review

## After Merge
- [ ] Delete feature branch
- [ ] Close related issues
- [ ] Monitor for any issues in main branch
- [ ] Celebrate! 🎉
