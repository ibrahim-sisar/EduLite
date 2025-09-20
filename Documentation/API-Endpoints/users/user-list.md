# List All Users

Retrieves a paginated list of all registered users.

## Endpoint URL

`/api/users/`

## HTTP Method

`GET`

## Permissions

* **Requires Authentication**: Yes
  * Only authenticated users can access this endpoint.
  * If the request is made by an unauthenticated user, a `401 Unauthorized` response will be returned.

## Request Headers

| Header        | Value                 | Required | Description                                     |
| :------------ | :-------------------- | :------- | :---------------------------------------------- |
| `Authorization` | `Bearer <access_token>` | Yes      | For token-based authentication.                 |
| `Content-Type`  | `application/json`    | No       | Not strictly required for GET, but good practice. |

## Query Parameters

| Parameter | Type    | Optional | Description                                      | Default |
| :-------- | :------ | :------- | :----------------------------------------------- | :------ |
| `page`    | Integer | Yes      | A page number within the paginated result set.   | 1       |
| `page_size`| Integer | Yes      | Number of results to return per page.           | 10 (as set in `UserListView`) |

*Note: While `page_size` can sometimes be overridden by the client if the pagination class is configured to allow it, the default for this view is 10.*

## Request Body

No request body is required for a `GET` request to this endpoint.

## Successful Response

**Status Code:** `200 OK`

The response will be a paginated JSON object containing a list of users. Each user object in the `results` array will conform to the `UserSerializer` structure.

**Example JSON Response:**

```json
{
    "count": 100,
    "next": "/api/users/?page=2",
    "previous": null,
    "results": [
        {
            "url": "/api/users/1/",
            "profile_url": "/api/users/1/profile/",
            "username": "sampleUser1",
            "email": "user1@example.com",
            "groups": [
                "/api/groups/1/"
            ]
        },
        {
            "url": "/api/users/2/",
            "profile_url": "/api/users/2/profile/",
            "username": "anotherUser",
            "email": "user2@example.com",
            "groups": []
        }
    ]
}
```

**Response Fields (Paginated Structure):**

| Field      | Type   | Description                                                                  |
| :--------- | :----- | :--------------------------------------------------------------------------- |
| `count`    | Integer| The total number of users available.                                         |
| `next`     | String | URL to the next page of results, or `null` if this is the last page.         |
| `previous` | String | URL to the previous page of results, or `null` if this is the first page.    |
| `results`  | Array  | An array of user objects. Each object contains the fields defined below.     |

**Response Fields (User Object in `results`):**

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
