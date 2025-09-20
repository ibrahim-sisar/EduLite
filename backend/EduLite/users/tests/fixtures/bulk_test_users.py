# users/tests/fixtures/bulk_test_users.py - Bulk user creation for performance testing

from django.contrib.auth.models import User
from django.db import transaction
import random
import string


def create_bulk_test_users(prefix="test", count=50):
    """
    Create multiple test users efficiently for performance testing.

    Args:
        prefix: String prefix for usernames (default: 'test')
        count: Number of users to create (default: 50)

    Returns:
        List of created User objects with profiles
    """
    users = []

    # Generate unique usernames
    usernames = []
    for i in range(count):
        # Add random suffix to ensure uniqueness
        suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
        username = f"{prefix}_user_{i}_{suffix}"
        usernames.append(username)

    # Use transaction for better performance
    with transaction.atomic():
        # Create users in bulk
        for username in usernames:
            user = User.objects.create_user(
                username=username,
                email=f"{username}@test.com",
                password="testpass123",
                first_name=f"Test",
                last_name=f"User",
            )

            # Configure profile with varied settings for realistic testing
            profile = user.profile

            # Vary countries for diversity
            countries = [
                "CA",
                "US",
                "FR",
                "NG",
                "BR",
                "IN",
                "PS",
                "RO",
                "MX",
                "KE",
                "UA",
                "GB",
                "DE",
                "JP",
                "AU",
            ]
            profile.country = random.choice(countries)

            # Vary languages
            languages = [
                "en",
                "fr",
                "es",
                "ar",
                "pt",
                "hi",
                "ro",
                "uk",
                "sw",
                "de",
                "ja",
                "zh",
            ]
            profile.preferred_language = random.choice(languages)

            # Vary occupations
            occupations = [
                "student",
                "teacher",
                "student",
                "student",
            ]  # More students than teachers
            profile.occupation = random.choice(occupations)

            # Add bio
            profile.bio = f"Test user from {profile.country}. Part of bulk test data."

            # Vary privacy settings for realistic testing
            if i % 4 == 0:
                # 25% private users
                profile.privacy_settings.search_visibility = "nobody"
                profile.privacy_settings.profile_visibility = "private"
                profile.privacy_settings.allow_friend_requests = False
            elif i % 4 == 1:
                # 25% friends only
                profile.privacy_settings.search_visibility = "friends_only"
                profile.privacy_settings.profile_visibility = "friends_only"
            elif i % 4 == 2:
                # 25% friends of friends
                profile.privacy_settings.search_visibility = "friends_of_friends"
                profile.privacy_settings.profile_visibility = "friends_only"
            else:
                # 25% public
                profile.privacy_settings.search_visibility = "everyone"
                profile.privacy_settings.profile_visibility = "public"
                profile.privacy_settings.show_email = True

            profile.privacy_settings.save()
            profile.save()

            users.append(user)

    # Create some friend relationships for realistic testing
    # Each user friends with 0-5 random other users
    with transaction.atomic():
        for i, user in enumerate(users):
            # Determine number of friends (most have 1-3, some have none, few have many)
            if i % 10 == 0:
                num_friends = 0  # 10% have no friends
            elif i % 5 == 0:
                num_friends = random.randint(4, 6)  # 10% have many friends
            else:
                num_friends = random.randint(1, 3)  # 80% have 1-3 friends

            # Select random friends
            if num_friends > 0 and len(users) > 1:
                potential_friends = [u for u in users if u != user]
                friends_to_add = random.sample(
                    potential_friends, min(num_friends, len(potential_friends))
                )

                for friend in friends_to_add:
                    # Make friendship mutual
                    user.profile.friends.add(friend)
                    friend.profile.friends.add(user)

    return users


def create_users_with_search_patterns(count=20):
    """
    Create users with specific patterns useful for search testing.

    Returns users with varied:
    - Names (common prefixes/suffixes)
    - Locations
    - Privacy settings
    - Friend relationships
    """
    # Common name patterns for search testing
    first_names = [
        "John",
        "Jane",
        "Ahmed",
        "Maria",
        "Li",
        "Sarah",
        "Mohamed",
        "Anna",
        "David",
        "Emma",
    ]
    last_names = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Garcia",
        "Miller",
        "Davis",
        "Rodriguez",
        "Martinez",
    ]

    users = []

    with transaction.atomic():
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}_{last_name.lower()}_{i}"

            user = User.objects.create_user(
                username=username,
                email=f"{username}@test.com",
                password="testpass123",
                first_name=first_name,
                last_name=last_name,
            )

            # Set up profile
            profile = user.profile
            profile.bio = (
                f"{first_name} {last_name} - Test user for search functionality"
            )

            # Vary search visibility
            visibility_options = [
                "everyone",
                "friends_only",
                "friends_of_friends",
                "nobody",
            ]
            profile.privacy_settings.search_visibility = visibility_options[i % 4]
            profile.privacy_settings.save()
            profile.save()

            users.append(user)

    return users


def create_friend_request_test_data(num_users=10, num_requests=15):
    """
    Create users with pending friend requests for testing.

    Args:
        num_users: Number of users to create
        num_requests: Number of friend requests to create

    Returns:
        Tuple of (users, friend_requests)
    """
    from ...models import ProfileFriendRequest

    # Create users
    users = create_bulk_test_users(prefix="fr_test", count=num_users)

    friend_requests = []

    with transaction.atomic():
        # Create friend requests between random pairs
        for _ in range(num_requests):
            sender = random.choice(users)
            receiver = random.choice(users)

            # Avoid self-requests and duplicates
            if sender != receiver:
                # Check if request already exists
                existing = ProfileFriendRequest.objects.filter(
                    sender=sender.profile, receiver=receiver.profile
                ).exists()

                if not existing:
                    request = ProfileFriendRequest.objects.create(
                        sender=sender.profile,
                        receiver=receiver.profile,
                        message=f"Hi! Let's connect and study together.",
                    )
                    friend_requests.append(request)

    return users, friend_requests
