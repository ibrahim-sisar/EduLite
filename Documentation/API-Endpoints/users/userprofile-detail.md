# Retrieve or Update User Profile

Allows an authenticated user to retrieve, fully update (`PUT`), or partially update (`PATCH`) a specific user profile. The `pk` in the URL refers to the ID of the `UserProfile` object.

## Endpoint URL

`/api/users/<int:pk>/profile/`

Replace `<int:pk>` with the unique ID of the `UserProfile` object.

## HTTP Methods

* `GET`: Retrieves the details of a specific user profile.
* `PUT`: Fully updates a user profile. All writable fields should be provided.
* `PATCH`: Partially updates a user profile. Only the fields to be changed need to be provided.

## Permissions

* **Requires Authentication**: Yes (`permissions.IsAuthenticated`)
  * Only authenticated users can access this endpoint.
  * TODO: Make it so they can only update their own profile.

## URL Parameters

| Parameter | Type    | Required | Description                                     |
| :-------- | :------ | :------- | :---------------------------------------------- |
| `pk`      | Integer | Yes      | The unique identifier of the UserProfile object. |

## Request Headers

| Header        | Value                 | Required                                   | Description                                                |
| :------------ | :-------------------- | :----------------------------------------- | :--------------------------------------------------------- |
| `Authorization` | `Bearer <access_token>` | Yes                                        | For token-based authentication.                            |
| `Content-Type`  | `application/json`    | Yes (for `PUT` and `PATCH` methods)         | Specifies that the request body is in JSON format.         |
## `GET` - Retrieve User Profile

Retrieves the details of the specified user profile.

**Successful `GET` Response:**

**Status Code:** `200 OK`

The response will contain a JSON object representing the user profile.

**Example `GET` JSON Response:**

```json
{
    "url": "/api/users/1/profile/",
    "user_url": "/api/users/1/",
    "bio": "Loves coding and hiking.",
    "occupation": "Software Developer",
    "country": "Canada",
    "preferred_language": "en",
    "secondary_language": "fr",
    "picture": "/media/profile_pics/user1.jpg",
    "friends": [
        "/api/users/2/profile/",
        "/api/users/3/profile/"
    ]
}
```

---

## `PUT` - Full Update User Profile

Fully replaces the user profile resource with the provided data. All writable fields should be included.

**Request Body Writable Fields (from `ProfileSerializer`):**

| Field                | Type         | Description                                                                |
| :------------------- | :----------- | :------------------------------------------------------------------------- |
| `bio`                | String       | A short biography of the user.                                             |
| `occupation`         | String       | The user's occupation.                                                     |
| `country`            | String       | The user's country of residence.                                           |
| `preferred_language` | String       | The user's preferred language (e.g., language code like 'en', 'es').       |
| `secondary_language` | String       | The user's secondary language (optional).                                  |
| `picture`            | String (URL/Path) | URL or path to the user's profile picture.                             |
| `friends`            | Array of URLs| A list of URLs pointing to the profiles of users considered friends.       |

*Note: `url` and `user_url` are read-only and generated by the server.*

**Example `PUT` Request Body:**

```json
{
    "bio": "Passionate about open source and rock climbing.",
    "occupation": "Senior Software Engineer",
    "country": "Canada",
    "preferred_language": "en",
    "secondary_language": "de",
    "picture": "/media/profile_pics/user1_new.jpg",
    "friends": [
        "/api/users/2/profile/"
    ]
}
```

**Successful `PUT` Response:**

**Status Code:** `200 OK`

The response will contain the full JSON object of the updated user profile.

**Example `PUT` JSON Response (reflecting changes):**

```json
{
    "url": "/api/users/1/profile/",
    "user_url": "/api/users/1/",
    "bio": "Passionate about open source and rock climbing.",
    "occupation": "Senior Software Engineer",
    "country": "Canada",
    "preferred_language": "en",
    "secondary_language": "de",
    "picture": "/media/profile_pics/user1_new.jpg",
    "friends": [
        "/api/users/2/profile/"
    ]
}
```

---

## `PATCH` - Partial Update User Profile

Partially updates the user profile resource. Only include the fields in the request body that you want to change.

**Example `PATCH` Request Body (updating only `occupation` and `bio`):**

```json
{
    "occupation": "Lead Developer",
    "bio": "Focusing on AI and machine learning."
}
```

**Successful `PATCH` Response:**

**Status Code:** `200 OK`

The response will contain the full JSON object of the updated user profile.

**Example `PATCH` JSON Response (reflecting changes):**

```json
{
    "url": "/api/users/1/profile/",
    "user_url": "/api/users/1/",
    "bio": "Focusing on AI and machine learning.",
    "occupation": "Lead Developer",
    "country": "Canada",
    "preferred_language": "en",
    "secondary_language": "de",
    "picture": "/media/profile_pics/user1_new.jpg",
    "friends": [
        "/api/users/2/profile/"
    ]
}
```

---

## Common Error Responses

* **Status Code:** `400 Bad Request`
  * **Reason (for `PUT`/`PATCH`):** The provided data is invalid (e.g., incorrect data type, invalid choices for fields with predefined options if any).
  * **Response Body (Example - Invalid data format):**

```json
{
    "preferred_language": [
        "\"french\" is not a valid choice."
    ],
    "friends": [
        "Invalid hyperlink - No URL match."
    ]
}
```

* **Status Code:** `401 Unauthorized`
  * **Reason:** Authentication credentials were not provided or were invalid.
  * **Response Body:**

```json
{
    "detail": "Authentication credentials were not provided."
}
```

* **Status Code:** `403 Forbidden`
  * **Reason:** The authenticated user does not have permission to access or modify this specific profile (e.g., if trying to modify another user's profile and object-level permissions deny this).
  * **Response Body:**

```json
{
    "detail": "You do not have permission to perform this action."
}
```

* **Status Code:** `404 Not Found`
  * **Reason:** A `UserProfile` with the specified `pk` does not exist.
  * **Response Body:**

```json
{
    "detail": "Not found."
}
```
