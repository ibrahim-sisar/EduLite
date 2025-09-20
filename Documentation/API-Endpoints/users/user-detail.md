# Retrieve User Details

Provides detailed information about a specific user.

## Endpoint URL

`/api/users/<int:pk>/`

Replace `<int:pk>` with the unique ID of the user you want to retrieve.

## HTTP Method

`GET`

## Permissions

* **Requires Authentication**: Yes
  * Only authenticated users can access this endpoint.
  * If the request is made by an unauthenticated user, a `401 Unauthorized` response will be returned.

## URL Parameters

| Parameter | Type    | Required | Description                             |
| :-------- | :------ | :------- | :-------------------------------------- |
| `pk`      | Integer | Yes      | The unique identifier of the user.    |

## Request Headers

| Header        | Value                 | Required | Description                                     |
| :------------ | :-------------------- | :------- | :---------------------------------------------- |
| `Authorization` | `Bearer <access_token>` | Yes      | For token-based authentication.                 |
| `Content-Type`  | `application/json`    | No       | Not strictly required for GET, but good practice. |

## Request Body

No request body is required for a `GET` request to this endpoint.

## Successful Response

**Status Code:** `200 OK`

The response will contain a JSON object representing the user, including hyperlinks to related resources like their profile and groups.

**Example JSON Response:**

```json
{
    "url": "/api/users/1/",
    "profile_url": "/api/users/1/profile/",
    "username": "sampleUser",
    "email": "user@example.com",
    "groups": [
        "/api/groups/1/",
        "/api/groups/2/"
    ]
}
```

**Response Fields:**

| Field         | Type   | Description                                                                 |
| :------------ | :----- | :-------------------------------------------------------------------------- |
| `url`         | String | The hyperlink to this user resource.                                        |
| `profile_url` | String | The hyperlink to the user's profile resource. Can be `null` if no profile. |
| `username`    | String | The username of the user.                                                   |
| `email`       | String | The email address of the user.                                              |
| `groups`      | Array  | A list of hyperlinks to the groups the user belongs to.                     |

## Error Responses

* **Status Code:** `401 Unauthorized`
  * **Reason:** Authentication credentials were not provided or were invalid.
  * **Response Body:**

```json
{
    "detail": "Authentication credentials were not provided."
}
```

* **Status Code:** `404 Not Found`
  * **Reason:** A user with the specified `pk` does not exist.
  * **Response Body:**

```json
{
    "detail": "Not found."
}
```

* **Status Code:** `403 Forbidden`
  * **Reason:** Although `IsAuthenticated` is the primary check, if object-level permissions were implemented and denied access (not the case for the current `UserRetrieveView` without `check_object_permissions` in `get`), this could occur.
  * **Response Body (Example):**

```json
{
    "detail": "You do not have permission to perform this action."
}
```
