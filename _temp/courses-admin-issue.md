---
name: "Newbie Backend Task"
about: "A beginner-friendly backend (Django/Python) task for EduLite contributors."
title: "[NEWBIE-BACKEND] Add Django Admin Interface for Courses App"
labels: 'good first issue, backend, help wanted'
assignees: ''

---
## Claiming This Task:

Please read the [Git Workflow Wiki Page](https://github.com/ibrahim-sisar/EduLite/wiki/Development-Git-Workflow) for updated community documentation.

Before you start working, please check the **Assignees** section on the right. If no one is assigned, leave a comment claiming the issue and assign it to yourself. This is required to prevent duplicate work.

## **🎯 Goal / Objective**

Add a professional Django admin interface for the courses app models (`Course`, `CourseModule`, `CourseMembership`, `CourseChatRoom`). Currently `backend/EduLite/courses/admin.py` is empty - your job is to make course management easy through Django's admin panel.

## **📝 Task Description / Requirements**

1. Open `backend/EduLite/courses/admin.py` (currently only 4 lines).

2. **Register CourseAdmin** with:
   - `list_display`: title, visibility, is_active, start_date, subject
   - `list_filter`: visibility, is_active, subject, language, country
   - `search_fields`: title, outline
   - `fieldsets`: Group fields into "Basic Information", "Visibility & Access", and "Schedule"
   - Include `CourseModuleInline` and `CourseMembershipInline`

3. **Create CourseModuleInline** (TabularInline):
   - Show modules within course admin
   - Display: order, title, content_type, object_id

4. **Create CourseMembershipInline** (TabularInline):
   - Show members within course admin
   - Display: user, role, status

5. **Register CourseMembershipAdmin**:
   - `list_display`: user, course, role, status
   - `list_filter`: role, status, course
   - `search_fields`: user__username, course__title

6. **Register CourseChatRoomAdmin**:
   - `list_display`: course, chatroom, created_by
   - `list_filter`: course
   - `readonly_fields`: created_by (can't change creator)

## **✨ Benefits / Why this helps EduLite**

Administrators can manage courses, modules, and memberships through a user-friendly interface instead of writing database scripts. This follows the same professional pattern used in the `slideshows` app and makes EduLite easier to maintain.

## **🛠️ Skills Required**

- Basic Python syntax
- Django ModelAdmin and admin customization
- Understanding Django model relationships (ForeignKey)
- Familiarity with inlines and fieldsets (you'll learn!)
- Git and GitHub for submitting a pull request

## **📚 Helpful Resources / Getting Started**

- **Best Reference**: `backend/EduLite/slideshows/admin.py` - Professional example with inlines and fieldsets
- **Another Example**: `backend/EduLite/users/admin.py` - Advanced admin techniques
- Django Admin Documentation: https://docs.djangoproject.com/en/5.2/ref/contrib/admin/
- Django Admin Inlines: https://docs.djangoproject.com/en/5.2/ref/contrib/admin/#inlinemodeladmin-objects
- Relevant Files: `backend/EduLite/courses/models.py`, `backend/EduLite/courses/admin.py`
- EduLite Contributing Guide: `CONTRIBUTING.md`
- Feel free to ask questions in our Discord server's #backend channel!

## **💻 Files to be Altered or Created (if known)**

- `backend/EduLite/courses/admin.py` - Main file to modify

## **🧪 Testing Considerations (Optional)**

Manual testing in Django admin panel:
1. Run `python manage.py runserver` from `backend/EduLite/`
2. Navigate to `http://localhost:8000/admin/`
3. Verify you can see and manage courses with filters, search, and inlines
4. Test creating a course with modules and memberships inline
5. Verify CourseMembership and CourseChatRoom admins work correctly

## **💡 Additional Context / Tips (Optional)**

Study `backend/EduLite/slideshows/admin.py` first - it's your blueprint! Notice how it uses fieldsets (lines 39-60) and inlines (lines 13-26). Start simple by registering models, then add features incrementally. Remember to import all models at the top. The admin interface you build will be used by real EduLite administrators!

---
*This task is designed as a good entry point for new backend contributors. We're here to support you through the process!*
