# Obtain Token Pair (Login)

Allows a registered user to obtain a JWT (JSON Web Token) access token and refresh token by providing their valid credentials (username and password). This is typically used as the login mechanism.

## Endpoint URL

`/api/token`

## HTTP Method

`POST`

## Permissions

* **Requires Authentication**: No
  * This endpoint is open and does not require prior authentication, as its purpose is to authenticate the user and issue tokens.

## Request Headers

| Header         | Value              | Required | Description                                       |
| :------------- | :----------------- | :------- | :------------------------------------------------ |
| `Content-Type` | `application/json` | Yes      | Specifies that the request body is in JSON format. |

## Request Body

The request body must be a JSON object containing the user's credentials.

**Fields:**

| Field      | Type   | Required | Description                       |
| :--------- | :----- | :------- | :-------------------------------- |
| `username` | String | Yes      | The registered username of the user. |
| `password` | String | Yes      | The user's password.              |

**Example Request Body:**

```json
{
    "username": "sampleUser",
    "password": "userpassword123"
}
```

## Successful Response

**Status Code:** `200 OK`

Upon successful authentication, the API will return a JSON object containing an `access` token and a `refresh` token.

* **Access Token**: This token is used to authenticate subsequent requests to protected API endpoints. It is typically short-lived.
* **Refresh Token**: This token is used to obtain a new access token once the current access token expires, without requiring the user to re-enter their credentials. It is typically longer-lived.

**Example JSON Response:**

```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcxNjYxMzk4MywiaWF0IjoxNzE2NTI3NTgzLCJqdGkiOiJhYmNkZWZnMTIzNDU2Nzg5IiwidXNlcl9pZCI6MX0.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE2NTI3ODYzLCJpYXQiOjE3MTY1Mjc1ODMsImp0aSI6IjEyMzQ1Njc4OWFiY2RlZmciLCJ1c2VyX2lkIjoxfQ.yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
}
```

## Error Responses

* **Status Code:** `400 Bad Request`
  * **Reason:** Required fields (`username` or `password`) are missing from the request body.
  * **Response Body (Example):**

```json
{
    "username": [
        "This field is required."
    ],
    "password": [
        "This field is required."
    ]
}
```

* **Status Code:** `401 Unauthorized`
  * **Reason:** Invalid credentials. No active account found with the given credentials (e.g., incorrect username or password).
  * **Response Body:**

```json
{
    "detail": "No active account found with the given credentials"
}
```
