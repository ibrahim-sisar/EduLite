# Retrieve Chat Message Details

Allows an authenticated user to retrieve details of a specific message within a chat room. The user must be a participant in the chat room to access message details.

## Endpoint URL

`api/chat/rooms/<int:chat_room_id>/messages/<int:pk>/`

Replace `<int:chat_room_id>` with the unique ID of the chat room and `<int:pk>` with the unique ID of the message.

## HTTP Methods

* `GET`: Retrieves the details of a specific message.
* `PUT`: Updates a message (full update, sender only).
* `PATCH`: Partially updates a message (sender only).
* `DELETE`: Deletes a message (sender only).

## Permissions

* **Requires Authentication**: Yes (`permissions.IsAuthenticated`)
* **Message Access**: Yes (`IsMessageSenderOrReadOnly`)
  * Only authenticated users who are participants in the chat room can view messages.
  * Only the message sender can update or delete messages.

## URL Parameters

| Parameter      | Type    | Required | Description                             |
|:---------------|:--------|:---------|:----------------------------------------|
| `chat_room_id` | Integer | Yes      | The unique identifier of the chat room. |
| `pk`           | Integer | Yes      | The unique identifier of the message.   |

## Request Headers

| Header          | Value                   | Required | Description                     |
|:----------------|:------------------------|:---------|:--------------------------------|
| `Authorization` | `Bearer <access_token>` | Yes      | For token-based authentication. |

---

## `GET` - Retrieve Message Details

Retrieves the details of the specified message if the authenticated user is a participant in the chat room.

**Successful `GET` Response:**

**Status Code:** `200 OK`

**Example `GET` JSON Response:**

```json
{
  "id": 1,
  "chat_room": 1,
  "sender": "edulite",
  "content": "Hello, EduLite!",
  "created_at": "2023-10-01T12:00:00Z",
  "is_read": false
}
```

---
## `PUT` - Update Message

Updates all fields of a message. Only the message sender can perform this action.

**Request Body:**

```json
{
  "content": "Updated message content"
}
```

**Successful `PUT` Response:**

**Status Code:** `200 OK`

**Example `PUT` JSON Response:**

```json
{
  "id": 1,
  "chat_room": 1,
  "sender": "edulite",
  "content": "Updated message content",
  "created_at": "2023-10-01T12:00:00Z",
  "is_read": false
}
```

---

## `PATCH` - Partially Update Message

Updates specific fields of a message. Only the message sender can perform this action.

**Request Body:**

```json
{
  "content": "Partially updated content"
}
```

**Successful `PATCH` Response:**

**Status Code:** `200 OK`

**Example `PATCH` JSON Response:**

```json
{
  "id": 1,
  "chat_room": 1,
  "sender": "edulite",
  "content": "Partially updated content",
  "created_at": "2023-10-01T12:00:00Z",
  "is_read": false
}
```

---

## `DELETE` - Delete Message

Deletes a message. Only the message sender can perform this action.

**Successful `DELETE` Response:**

**Status Code:** `204 No Content`

**Example `DELETE` Response:**

No content is returned in the response body.

---

## Common Error Responses

* **Status Code:** `400 Bad Request`
  * **Reason:** The provided data is invalid (e.g., `content` field missing or not a string).
  * **Response Body:**

```json
{
    "content": [
        "This field is required."
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
    * **Reason:** A `Chat Room` with the specified `chat_room_id` does not exist.
    * **Response Body:**

```json
{
    "detail": "You do not have permission to perform this action."
}
```

* **Status Code:** `404 Not Found`
  * **Reason:** A `Message` with the specified `pk` does not exist.
  * **Response Body:**

```json
{
    "detail":"No Message matches the given query."
}
```
