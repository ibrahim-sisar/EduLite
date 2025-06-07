import random

from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError, models

from users.models import UserProfile, ProfileFriendRequest

from users.management.utils.faker_utils import (
    get_random_username,
    get_random_email,
    get_random_bio,
    get_random_first_name,
    get_random_last_name,
    get_random_occupation,
    get_random_country,
    get_random_language,
    get_random_profile_picture_path
)

User = get_user_model()

## -- Main Function for User Generation -- ##

def generate_dummy_users_data(num_users: int, password: str):
    """
    Main orchestrator function to generate a specified number of dummy users
    and establish random friendships between them.
    """
    # Step 1: Prepare configuration data
    config = _prepare_dummy_data_config()
    
    # Step 2: Create users in a loop
    print(f"\nPhase B: Attempting to create {num_users} dummy user(s)...")
    created_users_list = []
    failed_count = 0

    for _ in range(num_users):
        user = _create_single_dummy_user(password, config)
        if user:
            created_users_list.append(user)
        else:
            failed_count += 1
    
    created_count = len(created_users_list)
    print(f"Phase B: User creation finished. {created_count} created, {failed_count} failed/skipped.")

    # Step 3: Establish random friendships using the previously refactored function
    establish_random_friendships(created_users_list)

    return created_count, failed_count

## -- Two Helper Functions for Generating Dummy Users Data -- ##

def _prepare_dummy_data_config() -> dict:
    """
    Prepares and returns a configuration dictionary with data choices
    needed for dummy user creation.
    """
    print("Phase A: Preparing configuration and data choices...")
    

    config = {
        'country_options': get_choices_from_field(UserProfile, 'country'),
        'occupation_options': get_choices_from_field(UserProfile, 'occupation'),
        'language_options': get_choices_from_field(UserProfile, 'preferred_language'),
        'dummy_picture_paths': [
            'profile_pics/dummy/avatar1.png',
            'profile_pics/dummy/avatar2.png',
            'profile_pics/dummy/avatar3.png',
        ]
    }
    print("Phase A: Configuration prepared.")
    return config


def _create_single_dummy_user(password: str, config: dict):
    """
    Creates a single dummy user with a populated profile.
    
    Args:
        password: The password to assign to the new user.
        config: A dictionary of data choices from _prepare_dummy_data_config.
        
    Returns:
        The created User instance, or None if creation failed.
    """
    username = get_random_username()
    email = get_random_email(username)
    
    try:
        with transaction.atomic():
            # Check for existing user first to avoid unnecessary create attempts
            if User.objects.filter(models.Q(username=username) | models.Q(email=email)).exists():
                print(f"  -Skipping user '{username}' as username or email already exists.")
                return None

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=get_random_first_name(),
                last_name=get_random_last_name(),
                is_active=True
            )
            
            # Populate UserProfile fields using faker_utils and config
            profile = user.profile # Use the related_name from User to get UserProfile
            profile.bio = get_random_bio()
            profile.occupation = get_random_occupation(config['occupation_options'])
            profile.country = get_random_country(config['country_options'])
            profile.preferred_language = get_random_language(config['language_options'])

            if random.choice([True, False]):
                profile.secondary_language = get_random_language(config['language_options'])
            
            if random.choice([True, False]):
                profile.picture = get_random_profile_picture_path(config['dummy_picture_paths'])

            profile.save()
            print(f"  -Successfully created user '{username}' and populated their profile.")
            return user
            
    except IntegrityError as e:
        print(f"  -Database integrity error for user '{username}': {e}. Skipping.")
    except Exception as e:
        print(f"  -An unexpected error occurred while creating user '{username}': {e}. Skipping.")
    
    return None


## -- Main Orchestation for Friend Request Simulation -- ##

def establish_random_friendships(users_list: list):
    """
    Simulates a realistic friendship creation process by orchestrating the
    creation and processing of friend requests.
    """
    if len(users_list) < 2:
        print("Not enough users to create friendships.")
        return

    # Step 1: Create a batch of pending friend requests
    new_requests = _create_pending_friend_requests(users_list)

    # Step 2: Process the newly created requests
    stats = _process_pending_friend_requests(new_requests)

    print(f"\nFriendship simulation complete. {stats.get('accepted_count', 0)} request(s) were accepted.")

## -- Two Helper Functions for Friend Request Simulation -- ##

def _create_pending_friend_requests(users_list: list) -> list:
    """
    Creates random pending friend requests between users in a provided list.

    This function is responsible for the 'sending' part of the simulation. It checks
    for pre-existing friendships or requests before creating new ones.

    Args:
        users_list: A list of User model instances.

    Returns:
        A list of the newly created ProfileFriendRequest model instances.
    """
    print("Phase 1: Sending random friend requests between dummy users...")
    newly_created_requests = []

    # Loop through each user to have them send some requests
    for sender_user in users_list:
        sender_profile = sender_user.profile

        # Identify potential users to send requests to (everyone except self)
        potential_receivers = [u for u in users_list if u.id != sender_user.id]
        if not potential_receivers:
            continue

        # Decide how many requests this user will send (e.g., 0 to 2)
        num_requests_to_send = random.randint(0, min(len(potential_receivers), 2))
        if num_requests_to_send == 0:
            continue

        receivers_to_request = random.sample(potential_receivers, num_requests_to_send)

        for receiver_user in receivers_to_request:
            receiver_profile = receiver_user.profile

            try:
                with transaction.atomic():
                    # Check if already friends (in either direction)
                    if sender_profile.friends.filter(pk=receiver_user.pk).exists() or \
                    receiver_profile.friends.filter(pk=sender_user.pk).exists():
                        continue  # Skip if already friends

                    # Check if a request already exists between them (in either direction)
                    if ProfileFriendRequest.objects.filter(
                        models.Q(sender=sender_profile, receiver=receiver_profile) |
                        models.Q(sender=receiver_profile, receiver=sender_profile)
                    ).exists():
                        continue  # Skip if a request already exists

                    # If all checks pass, create the friend request
                    request_instance = ProfileFriendRequest.objects.create(
                        sender=sender_profile,
                        receiver=receiver_profile
                    )
                    newly_created_requests.append(request_instance)
                    print(f"  -'{sender_user.username}' sent a friend request to '{receiver_user.username}'.")
            except IntegrityError:
                # This can happen in a race condition if the UniqueConstraint is hit.
                print(f"  -Skipping request from '{sender_user.username}' to '{receiver_user.username}' due to existing record.")
                continue
    
    return newly_created_requests


def _process_pending_friend_requests(pending_requests: list) -> dict:
    """
    Processes a list of pending friend requests by randomly accepting some of them.

    This function is responsible for the 'action' part of the simulation.

    Args:
        pending_requests: A list of ProfileFriendRequest model instances.

    Returns:
        A dictionary containing statistics about the actions taken.
    """
    if not pending_requests:
        print("\nPhase 2: No new friend requests were sent to process.")
        return {'accepted_count': 0, 'declined_count': 0}

    print("\nPhase 2: Randomly accepting/declining some of the pending friend requests...")
    accepted_count = 0
    declined_count = 0
    
    for request in pending_requests:
        # Randomly decide if the receiver accepts or ignores this request
        if random.choice([True, False]): # should they accept?
            print(f"  -'{request.receiver.user.username}' accepted the request from '{request.sender.user.username}'.")
            request.accept()  # Use the robust model method!
            accepted_count += 1
        elif random.choice([True, False]): # should they decline?
                request.decline()
                declined_count += 1
                print(f"  -'{request.receiver.user.username}' declined the request from '{request.sender.user.username}'.")
        else: # neither? just ignore
            print(f"  -'{request.receiver.user.username}' ignored the request from '{request.sender.user.username}'.")


    return {
        'accepted_count': accepted_count,
        'declined_count': declined_count
        }

## -- Small Utility Functions -- ##

def get_choices_from_field(model, field_name):
    field = model._meta.get_field(field_name)
    return [choice[0] for choice in getattr(field, 'choices', []) if choice[0]]