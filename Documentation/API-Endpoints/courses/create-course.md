# Create Course

Create a new course. The authenticated user is automatically added to the course roster with a `teacher` membership.

## Endpoint URL

`/api/courses/`

## HTTP Methods

* `POST`: Creates a new course.

## Permissions

* **Requires Authentication**: Yes (`permissions.IsAuthenticated`)
---

## `POST` – Create a Course

Create a course and associate yourself as the teacher.

**Request Headers:**

| Header | Value | Required | Description |
| :-- | :-- | :-- | :-- |
| `Authorization` | `Bearer <access_token>` | Yes | Token-based authentication. |
| `Content-Type` | `application/json` | Yes | Request body format. |

**Request Body Fields (from `CourseSerializer`):**

| Field | Type | Required | Description |
| :-- | :-- | :-- | :-- |
| `title` | String | Yes | Course title. Cannot be blank or whitespace only. Max 128 characters. |
| `outline` | String | No | Brief description (max 1000 characters). |
| `language` | String | No | Language code from supported choices (e.g. `en`). |
| `country` | String | No | Country code from supported choices (e.g. `US`). |
| `subject` | String | No | Subject identifier from supported choices (e.g. `physics`). |
| `visibility` | String | No | Course visibility; one of `public`, `private`, or `restricted`. Defaults to `private`. |
| `start_date` | DateTime | No | ISO 8601 timestamp for when the course becomes available. Defaults to current time. |
| `end_date` | DateTime | No | ISO 8601 timestamp when the course ends. Must be after `start_date`. Defaults to far-future sentinel. |
| `allow_join_requests` | Boolean | No | Whether students may request to join. Defaults to `false`. |

`is_active` and `duration_time` are read-only fields returned in the response.

**Example `POST` Request Body:**

```json
{
    "title": "Quantum Mechanics 101",
    "outline": "An introduction to quantum principles.",
    "language": "en",
    "country": "US",
    "subject": "physics",
    "visibility": "private",
    "start_date": "2024-09-01T08:00:00Z",
    "end_date": "2024-12-15T20:00:00Z",
    "allow_join_requests": true
}
```

**Successful `POST` Response:**

**Status Code:** `201 Created`

```json
{
    "id": 12,
    "title": "Quantum Mechanics 101",
    "outline": "An introduction to quantum principles.",
    "language": "en",
    "country": "US",
    "subject": "physics",
    "visibility": "private",
    "start_date": "2024-09-01T08:00:00Z",
    "end_date": "2024-12-15T20:00:00Z",
    "duration_time": 14880.0,
    "allow_join_requests": true,
    "is_active": false
}
```

---

## Common Error Responses

* **Status Code:** `400 Bad Request`
  * **Reason:** Validation error (e.g., `title` blank, `end_date` before `start_date`).
  * **Response Body Example:**

```json
{
    "title": [
        "Title cannot be all spaces."
    ]
}
```

* **Status Code:** `401 Unauthorized`
  * **Reason:** Authentication credentials missing or invalid.
  * **Response Body Example:**

```json
{
    "detail": "Authentication credentials were not provided."
}
```

### Additional Notes

* The authenticated creator is automatically enrolled in the new course with a `teacher` role and `enrolled` status.
* Use `/api/users/` endpoints to manage user profiles if occupation updates are required.
