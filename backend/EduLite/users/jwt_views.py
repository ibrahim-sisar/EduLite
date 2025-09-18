"""
Custom JWT views with OpenAPI documentation.
Extends Simple JWT views to add proper Swagger/ReDoc documentation.
"""

from rest_framework import serializers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiResponse,
    OpenApiExample
)


@extend_schema(
    summary="Login (Obtain JWT tokens)",
    description="""
    Authenticate with username and password to receive JWT access and refresh tokens.
    
    **Token Lifetimes:**
    - Access token: 5 minutes
    - Refresh token: 1 day
    
    Use the access token in the Authorization header for authenticated requests:
    `Authorization: Bearer <access_token>`
    """,
    request=inline_serializer(
        name='LoginRequest',
        fields={
            'username': serializers.CharField(help_text="Your username from registration"),
            'password': serializers.CharField(help_text="Your password (minimum 8 characters)")
        }
    ),
    examples=[
        OpenApiExample(
            'Login with Registered User',
            value={
                'username': 'johndoe123',
                'password': 'SecurePass123!'
            },
            request_only=True,
            description='Use the same credentials from registration'
        ),
        OpenApiExample(
            'Alternative Login',
            value={
                'username': 'janedoe456',
                'password': 'MyPassword2024'
            },
            request_only=True,
            description='Another valid login example'
        )
    ],
    responses={
        200: OpenApiResponse(
            description="Successfully authenticated",
            response=inline_serializer(
                name='TokenPairResponse',
                fields={
                    'access': serializers.CharField(help_text="JWT access token (expires in 5 minutes)"),
                    'refresh': serializers.CharField(help_text="JWT refresh token (expires in 1 day)")
                }
            ),
            examples=[
                OpenApiExample(
                    'Successful Login',
                    value={
                        'access': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk5ODg3NjAwLCJpYXQiOjE2OTk4ODczMDAsImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjoxfQ.abc123',
                        'refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY5OTk3NDAwMCwiaWF0IjoxNjk5ODg3MzAwLCJqdGkiOiI5ODc2NTQzMjEwIiwidXNlcl9pZCI6MX0.xyz789'
                    },
                    description='JWT tokens returned after successful authentication'
                )
            ]
        ),
        401: OpenApiResponse(
            description="Invalid credentials",
            response=inline_serializer(
                name='LoginError',
                fields={
                    'detail': serializers.CharField()
                }
            ),
            examples=[
                OpenApiExample(
                    'Invalid Credentials',
                    value={'detail': 'No active account found with the given credentials'}
                ),
                OpenApiExample(
                    'Account Inactive',
                    value={'detail': 'User account is disabled.'}
                )
            ]
        ),
        400: OpenApiResponse(
            description="Bad request - missing or invalid fields",
            response=inline_serializer(
                name='ValidationError',
                fields={
                    'username': serializers.ListField(child=serializers.CharField(), required=False),
                    'password': serializers.ListField(child=serializers.CharField(), required=False),
                }
            ),
            examples=[
                OpenApiExample(
                    'Missing Fields',
                    value={
                        'username': ['This field is required.'],
                        'password': ['This field is required.']
                    }
                )
            ]
        )
    },
    tags=['Authentication']
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token obtain pair view with OpenAPI documentation.
    Takes a set of user credentials and returns access and refresh JWT tokens.
    """
    pass


@extend_schema(
    summary="Refresh JWT token",
    description="""
    Get a new access token using a valid refresh token.
    
    When your access token expires (after 5 minutes), use this endpoint with your 
    refresh token to get a new access token without re-authenticating.
    
    **Note:** If token rotation is enabled, you'll also receive a new refresh token.
    """,
    request=inline_serializer(
        name='RefreshTokenRequest',
        fields={
            'refresh': serializers.CharField(help_text="Your refresh token from login")
        }
    ),
    examples=[
        OpenApiExample(
            'Refresh Token',
            value={
                'refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY5OTk3NDAwMCwiaWF0IjoxNjk5ODg3MzAwLCJqdGkiOiI5ODc2NTQzMjEwIiwidXNlcl9pZCI6MX0.xyz789'
            },
            request_only=True,
            description='Provide the refresh token received from login'
        )
    ],
    responses={
        200: OpenApiResponse(
            description="Successfully refreshed",
            response=inline_serializer(
                name='TokenRefreshResponse',
                fields={
                    'access': serializers.CharField(help_text="New JWT access token"),
                    'refresh': serializers.CharField(help_text="New JWT refresh token (if rotation enabled)", required=False)
                }
            ),
            examples=[
                OpenApiExample(
                    'New Access Token',
                    value={
                        'access': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk5ODg4MjAwLCJpYXQiOjE2OTk4ODc5MDAsImp0aSI6ImFiY2RlZmdoaWoiLCJ1c2VyX2lkIjoxfQ.newtoken123',
                        'refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY5OTk3NDYwMCwiaWF0IjoxNjk5ODg3OTAwLCJqdGkiOiJrbG1ub3BxcnN0IiwidXNlcl9pZCI6MX0.newrefresh456'
                    },
                    description='New tokens (refresh token included if rotation is enabled)'
                )
            ]
        ),
        401: OpenApiResponse(
            description="Invalid or expired refresh token",
            response=inline_serializer(
                name='RefreshError',
                fields={
                    'detail': serializers.CharField(),
                    'code': serializers.CharField(required=False)
                }
            ),
            examples=[
                OpenApiExample(
                    'Token Expired',
                    value={
                        'detail': 'Token is invalid or expired',
                        'code': 'token_not_valid'
                    }
                ),
                OpenApiExample(
                    'Token Blacklisted',
                    value={
                        'detail': 'Token is blacklisted',
                        'code': 'token_not_valid'
                    }
                )
            ]
        ),
        400: OpenApiResponse(
            description="Bad request - missing refresh token",
            response=inline_serializer(
                name='RefreshValidationError',
                fields={
                    'refresh': serializers.ListField(child=serializers.CharField())
                }
            ),
            examples=[
                OpenApiExample(
                    'Missing Refresh Token',
                    value={
                        'refresh': ['This field is required.']
                    }
                )
            ]
        )
    },
    tags=['Authentication']
)
class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view with OpenAPI documentation.
    Takes a refresh token and returns a new access token (and possibly a new refresh token).
    """
    pass