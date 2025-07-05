# List Chat Rooms or Create Chat Room

Allows an authenticated user to retrieve a paginated list of Chat rooms the user participates in or create a new chat room.

## Endpoint URL

`/api/chat/rooms/`

## HTTP Methods

* `GET`: Retrieves a paginated list of all chat rooms the user participates in.
* `POST`: Create a new chat room. Authenticated user is added as participant.

## Permissions

* **Requires Authentication**: Yes (`permissions.IsAuthenticated`)
    * Only authenticated users can access this endpoint.

* **Requires Participant Permission**: Yes (`permissions.IsParticipant`)
    * Only users who are participants in the chat rooms can access this endpoint.

---

## `GET` - List Chat Rooms

Retrieves a paginated list of all chat rooms the user participates in.

**Request Headers:**

| Header          | Value                   | Required | Description                     |
|:----------------|:------------------------|:---------|:--------------------------------|
| `Authorization` | `Bearer <access_token>` | Yes      | For token-based authentication. |

**Query Parameters:**

| Parameter   | Type    | Optional | Description                                    | Default                             |
|:------------|:--------|:---------|:-----------------------------------------------|:------------------------------------|
| `page`      | Integer | Yes      | A page number within the paginated result set. | 1                                   |
| `page_size` | Integer | Yes      | Number of results to return per page.          | 10 (as set in `ChatRoomPagination`) |

**Successful `GET` Response:**

**Status Code:** `200 OK`

The response will be a paginated JSON object containing a list of all chat rooms the user participates in.

**Example `GET` JSON Response:**

```json
{
  "next": "http://localhost:8000/api/chat/rooms/?page=1&page_size=10",
  "previous": null,
  "count": 1,
  "total_pages": 1,
  "current_page": 1,
  "results": [
    {
      "id": 1,
      "name": "General",
      "room_type": "GROUP",
      "participants": [1, 2],
      "messages": [
        {
          "id": 1,
          "chat_room": 1,
          "sender": 1,
          "sender_id": 1, 
          "content": "Hello, EduLite!",
          "created_at": "2023-10-01T12:00:00Z",
          "is_read": true
        }
      ],
      "created_at": "2025-07-05T16:44:51.889737Z",
      "updated_at": "2025-07-05T16:44:51.889737Z"
    }
  ],
  "page_size": 10
}
```

**Response Fields (Paginated Structure):**

| Field          | Type    | Description                                                                   |
|:---------------|:--------|:------------------------------------------------------------------------------|
| `next`         | String  | URL to the next page of results, or `null` if this is the last page.          |
| `previous`     | String  | URL to the previous page of results, or `null` if this is the first page.     |
| `count`        | Integer | The total number of chat rooms available.                                     |
| `total_pages`  | Integer | The total number of pages available based on `page_size`.                     |
| `current_page` | Integer | The current page number.                                                      |
| `results`      | Array   | An array of chat room objects. Each object contains the fields defined below. |
| `page_size`    | Integer | The number of results per page.                                               |

**Response Fields (Chat Room Object in `results`):**

| Field          | Type   | Description                                                    |
|:---------------|:-------|:---------------------------------------------------------------|
| `id`           | String | The unique identifier of the chat room.                        |
| `name`         | String | The name of the chat room.                                     |
| `room_type`    | String | The type of chat room (e.g., `ONE_TO_ONE`, `GROUP`, `COURSE`). |
| `participants` | Array  | List of user IDs who are participants in the chat room.        |
| `messages`     | Array  | List of messages in the chat room (if applicable).             |
| `created_at`   | String | Timestamp of when the chat room was created.                   |
| `updated_at`   | String | Timestamp of when the chat room was last updated.              |

---

## `POST` - Create Chat Room

Creates a new chat room. Authenticated user is added as participant.

**Request Headers:**

| Header          | Value                   | Required | Description                                        |
|:----------------|:------------------------|:---------|:---------------------------------------------------|
| `Authorization` | `Bearer <access_token>` | Yes      | For token-based authentication.                    |
| `Content-Type`  | `application/json`      | Yes      | Specifies that the request body is in JSON format. |

**Request Body:**

The request body must be a JSON object containing the details for the new chat room.

**Fields (from `ChatRoomSerializer`):**

| Field          | Type   | Description                                                    |
|:---------------|:-------|:---------------------------------------------------------------|
| `id`           | String | The unique identifier of the chat room.                        |
| `name`         | String | The name of the chat room.                                     |
| `room_type`    | String | The type of chat room (e.g., `ONE_TO_ONE`, `GROUP`, `COURSE`). |
| `participants` | Array  | List of user IDs who are participants in the chat room.        |
| `messages`     | Array  | List of messages in the chat room (if applicable).             |
| `created_at`   | String | Timestamp of when the chat room was created.                   |
| `updated_at`   | String | Timestamp of when the chat room was last updated.              |


| Field            | Type   | Required | Description                                                                                                                |
|:-----------------|:-------|:---------|:---------------------------------------------------------------------------------------------------------------------------|
| `name`           | String | Yes      | The name of the new group. Must be unique if database constraints enforce this.                                            |
| `participants`   | Array  | No       | List of user IDs to be added as participants in the chat room. If not provided, only the authenticated user will be added. |
| `room_type`      | String | Yes      | The type of chat room (e.g., `ONE_TO_ONE`, `GROUP`, `COURSE`).                                                             |

**Example `POST` Request Body:**

```json
{
  "id": 1,
  "name": "General",
  "room_type": "GROUP",
  "participants": [
    1,
    2
  ],
  "messages": [],
  "created_at": "2025-07-05T16:44:51.889737Z",
  "updated_at": "2025-07-05T16:44:51.889757Z"
}
```

**Successful `POST` Response:**

**Status Code:** `201 Created`

The response will contain the JSON object of the newly created group.

**Example `POST` JSON Response:**

```json
{
  "id": 5,
  "name": "New Room",
  "participants": [1, 2, 3]
}
```

---

## Common Error Responses
* **Status Code:** `400 Bad Request`
  * **Reason (for `POST`):** The provided data is invalid (e.g., `pk` for participant doesn't exist.
  * **Response Body (Example - `name` missing):**

```json
{
  "participants": [
    "Invalid pk \"6\" - object does not exist."
  ]
}
```

* **Status Code:** `400 Bad Request`
  * **Reason (for `POST`):** The provided data is invalid (e.g., `room_type` field missing).  
  * **Response Body (Example - `room_type` missing):**

```json
{
  "room_type": [
    "This field is required."
  ]
}
```

* **Status Code:** `400 Bad Request`
  * **Reason (for `POST`):** The provided data is invalid (e.g., `room_type` field not one of `ONE_TO_ONE`, `GROUP`, `COURSE`).
  * **Response Body (Example - `room_type` invalid):**

```json
{
  "room_type": [
    "\"\" is not a valid choice."
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
