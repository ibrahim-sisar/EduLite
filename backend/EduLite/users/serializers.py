from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import serializers

from .models import UserProfile, ProfileFriendRequest

User = get_user_model()


## -- Profile Serializers -- ##


class ProfileSerializer(serializers.HyperlinkedModelSerializer): # Or HyperlinkedModelSerializer if you prefer
    """
    Serializer for the UserProfile model.
    """
    user_url = serializers.HyperlinkedRelatedField(
        source='user',
        view_name='user-detail',
        read_only=True,
    )
    class Meta:
        model = UserProfile
        fields = [
            'url',       # URL for the UserProfile instance itself
            'user_url',  # URL for the related User instance
            'bio',
            'occupation',
            'country',
            'preferred_language',
            'secondary_language',
            'picture',
            'website_url',
            'friends', 
        ]


## -- User/Group Hyperlinked Serializers -- ##


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Group model.
    Exposes the 'url' (hyperlink to the group detail) and 'name' of the group.
    """
    class Meta:
        model = Group
        fields = ['id','url', 'name']
        # 'url' is automatically configured by HyperlinkedModelSerializer


class UserSerializer(serializers.HyperlinkedModelSerializer): # Or ModelSerializer
    """
    Serializer for the User model, now including nested profile information.
    """
    profile_url = serializers.HyperlinkedRelatedField(
        source='profile',
        view_name='userprofile-detail', 
        read_only=True, 
    )
    
    class Meta:
        model = User
        fields = [
            'id',
            'url',       # URL for the User instance itself
            'profile_url', # URL for the UserProfile instance
            'username',
            'email',
            'groups',   
            'first_name',
            'last_name',
        ]



## -- Secure Password Hashing Serializers -- ##


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles username, email, password input, password confirmation, and secure password hashing.
    """
    email = serializers.EmailField(required=True)
    
    password = serializers.CharField(
        write_only=True, # ensures the password is never returned in the response
        required=True, 
        validators=[validate_password] # validates that the password is strong enough
        )
    password2 = serializers.CharField(
        write_only=True, 
        required=True, 
        label="Confirm password"
        )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {
            # If we want users to optionally enter their names on registration:
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def validate_email(self, value: str) -> str:
        """
        Perform custom email validations:
        1. Check for blocked domains.
        2. Check for email uniqueness.
        """
        if '@' not in value:
            # This is an extra safeguard. EmailField should catch most format issues.
            raise serializers.ValidationError("Invalid email format: '@' symbol missing.")
        email_name, domain_part = value.split('@', 1)
        from django.conf import settings
        blocked_domains = getattr(settings, 'BLOCKED_EMAIL_DOMAINS', ['example.com', 'test.com'])
        
        if domain_part.lower() in [d.lower() for d in blocked_domains]:
            raise serializers.ValidationError(
                "Registration from this email domain is not allowed."
            )

        # Uniqueness Check
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this email address already exists."
            )
        
        return value # If all checks pass, return the validated email value

    def validate_username(self, value):
        """
        Check that the username is unique.
        """
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate(self, attrs):
        """
        Check that the two password entries match.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Password fields didn't match."})
        # You can add more custom validation here if needed
        return attrs

    def create(self, validated_data):
        """
        Create and return a new user instance, given the validated data.
        Handles password hashing.
        """
        # Remove password2 from validated_data as it's not part of the User model
        validated_data.pop('password2')
        
        # Extract password to use with create_user
        password = validated_data.pop('password')
        
        # create_user handles normalization of username/email and password hashing
        user = User.objects.create_user(
            **validated_data, # username, email, first_name, last_name
            password=password,
            is_active=True, # TODO: Setup email verification, or other means of account activation
        )
        return user


## -- Friend Request Serializers -- ##


class ProfileFriendRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProfileFriendRequest model.
    Represents a friend request for API output, including profile URLs.
    """    
    # Using SerializerMethodField to generate URLs
    sender_profile_url = serializers.SerializerMethodField()
    receiver_profile_url = serializers.SerializerMethodField()
    accept_url = serializers.SerializerMethodField()
    decline_url = serializers.SerializerMethodField()

    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = ProfileFriendRequest
        fields = [
            'id',
            'sender_id',   
            'receiver_id',  
            'sender_profile_url',
            'receiver_profile_url',
            'created_at',
            'accept_url',
            'decline_url',
        ]
        read_only_fields = ['id', 'created_at']

    def get_sender_profile_url(self, obj: ProfileFriendRequest) -> str | None:
        request = self.context.get('request')
        if request and obj.sender:
            return request.build_absolute_uri(
                reverse('userprofile-detail', kwargs={'pk': obj.sender.pk})
            )
        return None

    def get_receiver_profile_url(self, obj: ProfileFriendRequest) -> str | None:
        request = self.context.get('request')
        if request and obj.receiver:
            return request.build_absolute_uri(
                reverse('userprofile-detail', kwargs={'pk': obj.receiver.pk})
            )
        return None
    
    def get_accept_url(self, obj: ProfileFriendRequest) -> str | None:
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                reverse('friend-request-accept', kwargs={'request_pk': obj.pk})
            )
        return None
    
    def get_decline_url(self, obj: ProfileFriendRequest) -> str | None:
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                reverse('friend-request-decline', kwargs={'request_pk': obj.pk})
            )
        return None