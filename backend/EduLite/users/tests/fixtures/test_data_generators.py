# users/tests/fixtures/test_data_generators.py - Helper functions for creating test data

from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import timedelta
import random

from ...models import UserProfile, ProfileFriendRequest, UserProfilePrivacySettings


# --- Bulk Creation Functions (Optimized for Tests) ---


def create_students_bulk():
    """Create all student personas efficiently and return as dict."""
    students = {}

    # Gaza, Palestine - Computer Science student
    ahmad = User.objects.create_user(
        username="ahmad_gaza",
        email="ahmad@gaza-university.ps",
        password="testpass123",
        first_name="Ahmad",
        last_name="Al-Rashid",
    )
    ahmad.profile.bio = "Computer Science student in Gaza. Learning despite challenges."
    ahmad.profile.country = "PS"
    ahmad.profile.preferred_language = "ar"
    ahmad.profile.occupation = "student"
    ahmad.profile.privacy_settings.search_visibility = "friends_of_friends"
    ahmad.profile.privacy_settings.profile_visibility = "friends_only"
    ahmad.profile.privacy_settings.save()
    ahmad.profile.save()
    students["ahmad"] = ahmad

    # Syrian refugee in France
    marie = User.objects.create_user(
        username="marie_student",
        email="marie.dubois@refugeecamp.org",
        password="testpass123",
        first_name="Marie",
        last_name="Dubois",
    )
    marie.profile.bio = "Étudiante syrienne en France. Apprendre pour reconstruire."
    marie.profile.country = "FR"
    marie.profile.preferred_language = "fr"
    marie.profile.secondary_language = "ar"
    marie.profile.occupation = "student"
    marie.profile.privacy_settings.search_visibility = "everyone"
    marie.profile.privacy_settings.profile_visibility = "public"
    marie.profile.privacy_settings.save()
    marie.profile.save()
    students["marie"] = marie

    # Nigeria - limited data
    joy = User.objects.create_user(
        username="joy_student",
        email="joy.okoro@communitynet.ng",
        password="testpass123",
        first_name="Joy",
        last_name="Okoro",
    )
    joy.profile.bio = "First in my family to pursue higher education. Mobile data is expensive but knowledge is priceless."
    joy.profile.country = "NG"
    joy.profile.preferred_language = "en"
    joy.profile.occupation = "student"
    joy.profile.privacy_settings.search_visibility = "friends_only"
    joy.profile.privacy_settings.save()
    joy.profile.save()
    students["joy"] = joy

    # Rural Romania
    elena = User.objects.create_user(
        username="elena_student",
        email="elena.popescu@library.ro",
        password="testpass123",
        first_name="Elena",
        last_name="Popescu",
    )
    elena.profile.bio = "Rural Romania. One computer in our village library. Studying nursing to help my community."
    elena.profile.country = "RO"
    elena.profile.preferred_language = "ro"
    elena.profile.secondary_language = "en"
    elena.profile.occupation = "student"
    elena.profile.save()
    students["elena"] = elena

    # Indigenous Canada
    james = User.objects.create_user(
        username="james_student",
        email="james.littlebear@firstnation.ca",
        password="testpass123",
        first_name="James",
        last_name="Littlebear",
    )
    james.profile.bio = "Cree Nation, Northern Ontario. Satellite internet when weather permits. Preserving our culture through education."
    james.profile.country = "CA"
    james.profile.preferred_language = "en"
    james.profile.occupation = "student"
    james.profile.privacy_settings.search_visibility = "friends_of_friends"
    james.profile.privacy_settings.save()
    james.profile.save()
    students["james"] = james

    # Sudan
    fatima = User.objects.create_user(
        username="fatima_student",
        email="fatima.hassan@khartoumlibrary.sd",
        password="testpass123",
        first_name="Fatima",
        last_name="Hassan",
    )
    fatima.profile.bio = (
        "Medical student in Khartoum. Power cuts daily but determination is constant."
    )
    fatima.profile.country = "SD"
    fatima.profile.preferred_language = "ar"
    fatima.profile.secondary_language = "en"
    fatima.profile.occupation = "student"
    fatima.profile.save()
    students["fatima"] = fatima

    # Brazil favela
    miguel = User.objects.create_user(
        username="miguel_student",
        email="miguel.silva@favela.edu.br",
        password="testpass123",
        first_name="Miguel",
        last_name="Silva",
    )
    miguel.profile.bio = (
        "Rio favela. Sharing one phone with siblings. Dreams bigger than circumstances."
    )
    miguel.profile.country = "BR"
    miguel.profile.preferred_language = "pt"
    miguel.profile.secondary_language = "es"
    miguel.profile.occupation = "student"
    miguel.profile.privacy_settings.search_visibility = "friends_only"
    miguel.profile.privacy_settings.save()
    miguel.profile.save()
    students["miguel"] = miguel

    # Homeless, Paris
    sophie = User.objects.create_user(
        username="sophie_student",
        email="sophie.martin@secours-catholique.fr",
        password="testpass123",
        first_name="Sophie",
        last_name="Martin",
    )
    sophie.profile.bio = (
        "Homeless shelter in Paris. Using library computers. Education is my way out."
    )
    sophie.profile.country = "FR"
    sophie.profile.preferred_language = "fr"
    sophie.profile.secondary_language = "en"
    sophie.profile.occupation = "student"
    sophie.profile.privacy_settings.search_visibility = "nobody"
    sophie.profile.privacy_settings.profile_visibility = "private"
    sophie.profile.privacy_settings.allow_friend_requests = False
    sophie.profile.privacy_settings.save()
    sophie.profile.save()
    students["sophie"] = sophie

    # Ukraine displaced
    dmitri = User.objects.create_user(
        username="dmitri_student",
        email="dmitri.volkov@youth-center.ua",
        password="testpass123",
        first_name="Dmitri",
        last_name="Volkov",
    )
    dmitri.profile.bio = (
        "Displaced from Mariupol. Learning IT in Lviv shelter. Code is hope."
    )
    dmitri.profile.country = "UA"
    dmitri.profile.preferred_language = "uk"
    dmitri.profile.secondary_language = "ru"
    dmitri.profile.occupation = "student"
    dmitri.profile.privacy_settings.search_visibility = "friends_of_friends"
    dmitri.profile.privacy_settings.save()
    dmitri.profile.save()
    students["dmitri"] = dmitri

    # Mexico indigenous
    maria = User.objects.create_user(
        username="maria_student",
        email="maria.gonzalez@biblioteca-rural.mx",
        password="testpass123",
        first_name="Maria",
        last_name="González",
    )
    maria.profile.bio = "Oaxaca mountains. 2 hour walk to internet cafe. Indigenous rights through education."
    maria.profile.country = "MX"
    maria.profile.preferred_language = "es"
    maria.profile.secondary_language = "en"
    maria.profile.occupation = "student"
    maria.profile.save()
    students["maria"] = maria

    return students


def create_teachers_bulk():
    """Create all teacher personas efficiently and return as dict."""
    teachers = {}

    # Toronto, Canada - Inner city teacher
    sarah = User.objects.create_user(
        username="sarah_teacher",
        email="sarah.johnson@innercity-school.ca",
        password="testpass123",
        first_name="Sarah",
        last_name="Johnson",
    )
    sarah.profile.bio = "Teaching in Toronto's priority neighborhoods. Every student deserves quality education."
    sarah.profile.country = "CA"
    sarah.profile.preferred_language = "en"
    sarah.profile.secondary_language = "fr"
    sarah.profile.occupation = "teacher"
    sarah.profile.website_url = "https://equityineducation.ca"
    sarah.profile.privacy_settings.search_visibility = "everyone"
    sarah.profile.privacy_settings.profile_visibility = "public"
    sarah.profile.privacy_settings.show_email = True
    sarah.profile.privacy_settings.save()
    sarah.profile.save()
    teachers["sarah"] = sarah

    # Cairo, Egypt - Computer Science Professor
    ahmed = User.objects.create_user(
        username="dr_ahmed",
        email="ahmed.hassan@cairo-university.eg",
        password="testpass123",
        first_name="Ahmed",
        last_name="Hassan",
    )
    ahmed.profile.bio = (
        "Professor of Computer Science. Building bridges through online education."
    )
    ahmed.profile.country = "EG"
    ahmed.profile.preferred_language = "ar"
    ahmed.profile.secondary_language = "en"
    ahmed.profile.occupation = "teacher"
    ahmed.profile.privacy_settings.search_visibility = "everyone"
    ahmed.profile.privacy_settings.profile_visibility = "public"
    ahmed.profile.privacy_settings.show_email = True
    ahmed.profile.privacy_settings.save()
    ahmed.profile.save()
    teachers["ahmed"] = ahmed

    # Rural Nigeria - Mobile learning advocate
    okonkwo = User.objects.create_user(
        username="prof_okonkwo",
        email="chidi.okonkwo@rural-education.ng",
        password="testpass123",
        first_name="Chidi",
        last_name="Okonkwo",
    )
    okonkwo.profile.bio = (
        "Bringing quality education to rural Nigeria. Mobile learning advocate."
    )
    okonkwo.profile.country = "NG"
    okonkwo.profile.preferred_language = "en"
    okonkwo.profile.secondary_language = "ig"
    okonkwo.profile.occupation = "teacher"
    okonkwo.profile.privacy_settings.search_visibility = "everyone"
    okonkwo.profile.privacy_settings.profile_visibility = "public"
    okonkwo.profile.privacy_settings.save()
    okonkwo.profile.save()
    teachers["okonkwo"] = okonkwo

    return teachers


def setup_friend_relationships(students, teachers):
    """Set up realistic friend relationships between personas."""
    # Students often friend each other across geographic boundaries

    # Ahmad (Gaza) friends with Marie (Syria-France) - Middle Eastern connection
    students["ahmad"].profile.friends.add(students["marie"])
    students["marie"].profile.friends.add(students["ahmad"])

    # Joy (Nigeria) friends with Elena (Romania) - connected through online study group
    students["joy"].profile.friends.add(students["elena"])
    students["elena"].profile.friends.add(students["joy"])

    # James (Indigenous Canada) friends with Dmitri (Ukraine) - indigenous/refugee solidarity
    students["james"].profile.friends.add(students["dmitri"])
    students["dmitri"].profile.friends.add(students["james"])

    # Miguel (Brazil) friends with Maria (Mexico) - Spanish/Portuguese speakers
    students["miguel"].profile.friends.add(students["maria"])
    students["maria"].profile.friends.add(students["miguel"])

    # Fatima (Sudan) friends with Joy (Nigeria) - African students network
    students["fatima"].profile.friends.add(students["joy"])
    students["joy"].profile.friends.add(students["fatima"])

    # Teachers often friend students they mentor
    teachers["sarah"].profile.friends.add(students["james"])  # Canadian connection
    students["james"].profile.friends.add(teachers["sarah"])

    teachers["ahmed"].profile.friends.add(
        students["ahmad"]
    )  # Middle Eastern connection
    students["ahmad"].profile.friends.add(teachers["ahmed"])


# --- Individual Persona Functions (Keep for backward compatibility) ---


def create_student_ahmad():
    """
    Create Ahmad - Computer Science student from Gaza, Palestine.
    Represents students in conflict zones with limited connectivity.
    """
    user = User.objects.create_user(
        username="ahmad_gaza",
        email="ahmad@gaza-university.ps",
        password="testpass123",
        first_name="Ahmad",
        last_name="Al-Rashid",
    )

    user.profile.bio = "Computer Science student in Gaza. Learning despite challenges."
    user.profile.country = "PS"
    user.profile.preferred_language = "ar"
    user.profile.occupation = "student"
    user.profile.save()

    # Privacy settings - careful due to situation
    user.profile.privacy_settings.search_visibility = "friends_of_friends"
    user.profile.privacy_settings.profile_visibility = "friends_only"
    user.profile.privacy_settings.save()

    return user


def create_student_marie_quebec():
    """
    Create Marie - Indigenous student from rural Quebec, Canada.
    Represents indigenous communities with limited resources.
    """
    user = User.objects.create_user(
        username="marie_quebec",
        email="marie@firstnations-edu.ca",
        password="testpass123",
        first_name="Marie",
        last_name="Tremblay",
    )

    user.profile.bio = (
        "Innu student from northern Quebec. Preserving our culture through education."
    )
    user.profile.country = "CA"
    user.profile.preferred_language = "fr"
    user.profile.secondary_language = "en"
    user.profile.occupation = "student"
    user.profile.save()

    return user


def create_student_joy_nigeria():
    """
    Create Joy - Student from rural Nigeria.
    Represents African students with expensive mobile data.
    """
    user = User.objects.create_user(
        username="joy_nigeria",
        email="joy@communitynet.ng",
        password="testpass123",
        first_name="Joy",
        last_name="Okoro",
    )

    user.profile.bio = "First in my family to pursue higher education. Mobile data is expensive but knowledge is priceless."
    user.profile.country = "NG"
    user.profile.preferred_language = "en"
    user.profile.occupation = "student"
    user.profile.save()

    # More private due to data costs
    user.profile.privacy_settings.search_visibility = "friends_only"
    user.profile.privacy_settings.save()

    return user


def create_student_elena_romania():
    """
    Create Elena - Student from rural Romania.
    Represents European students in underserved areas.
    """
    user = User.objects.create_user(
        username="elena_romania",
        email="elena@library.ro",
        password="testpass123",
        first_name="Elena",
        last_name="Popescu",
    )

    user.profile.bio = "Rural Romania. One computer in our village library. Studying nursing to help my community."
    user.profile.country = "RO"
    user.profile.preferred_language = "ro"
    user.profile.secondary_language = "en"
    user.profile.occupation = "student"
    user.profile.save()

    return user


def create_student_refugee():
    """
    Create a refugee student profile.
    Represents displaced students worldwide.
    """
    user = User.objects.create_user(
        username="amal_refugee",
        email="amal@unhcr.org",
        password="testpass123",
        first_name="Amal",
        last_name="Hassan",
    )

    user.profile.bio = "Syrian refugee in Jordan. Education is hope for the future."
    user.profile.country = "JO"
    user.profile.preferred_language = "ar"
    user.profile.secondary_language = "en"
    user.profile.occupation = "student"
    user.profile.save()

    # Very open - looking for connections
    user.profile.privacy_settings.search_visibility = "everyone"
    user.profile.privacy_settings.profile_visibility = "public"
    user.profile.privacy_settings.save()

    return user


# --- Teacher Personas ---


def create_teacher_sarah():
    """
    Create Sarah - Teacher from inner-city Toronto, Canada.
    Represents educators serving underprivileged communities in developed countries.
    """
    user = User.objects.create_user(
        username="sarah_toronto",
        email="sarah@innercity-school.ca",
        password="testpass123",
        first_name="Sarah",
        last_name="Johnson",
    )

    user.profile.bio = "Teaching in Toronto's priority neighborhoods. Every student deserves quality education."
    user.profile.country = "CA"
    user.profile.preferred_language = "en"
    user.profile.secondary_language = "fr"
    user.profile.occupation = "teacher"
    user.profile.website_url = "https://equityineducation.ca"
    user.profile.save()

    # Teachers are generally more open
    user.profile.privacy_settings.search_visibility = "everyone"
    user.profile.privacy_settings.profile_visibility = "public"
    user.profile.privacy_settings.show_email = True
    user.profile.privacy_settings.save()

    return user


def create_teacher_multilingual():
    """
    Create a multilingual teacher serving refugee communities.
    """
    user = User.objects.create_user(
        username="fatou_teacher",
        email="fatou@refugee-education.org",
        password="testpass123",
        first_name="Fatou",
        last_name="Diallo",
    )

    user.profile.bio = "Teaching in refugee camps. Speaking French, Arabic, and English to reach all students."
    user.profile.country = "SN"
    user.profile.preferred_language = "fr"
    user.profile.secondary_language = "ar"
    user.profile.occupation = "teacher"
    user.profile.save()

    return user


# --- Test Scenarios ---


def create_test_class_with_students(teacher_username="test_teacher", num_students=10):
    """
    Create a complete class with teacher and diverse students.
    Represents a typical EduLite virtual classroom.
    """
    # Create teacher
    teacher = User.objects.create_user(
        username=teacher_username,
        email=f"{teacher_username}@edulite.org",
        password="testpass123",
        first_name="Test",
        last_name="Teacher",
    )
    teacher.profile.occupation = "teacher"
    teacher.profile.save()

    # Create diverse students
    countries = ["CA", "FR", "NG", "BR", "IN", "PS", "RO", "MX", "KE", "UA"]
    languages = ["en", "fr", "es", "ar", "pt", "hi", "ro", "uk", "sw", "de"]

    students = []
    for i in range(num_students):
        student = User.objects.create_user(
            username=f"student_{i}",
            email=f"student{i}@test.com",
            password="testpass123",
            first_name=f"Student",
            last_name=f"{i}",
        )

        # Assign diverse backgrounds
        student.profile.country = countries[i % len(countries)]
        student.profile.preferred_language = languages[i % len(languages)]
        student.profile.occupation = "student"
        student.profile.bio = f"Student from {student.profile.country}"
        student.profile.save()

        students.append(student)

    return teacher, students


def create_friend_network(num_users=6):
    """
    Create a network of users with existing friendships.
    Useful for testing friend-based features.
    """
    users = []

    # Create users
    for i in range(num_users):
        user = User.objects.create_user(
            username=f"network_user_{i}",
            email=f"network{i}@test.com",
            password="testpass123",
        )
        users.append(user)

    # Create friendships (each user friends with 2-3 others)
    for i, user in enumerate(users):
        # Friend with next 2 users (circular)
        friend1 = users[(i + 1) % num_users]
        friend2 = users[(i + 2) % num_users]

        user.profile.friends.add(friend1)
        user.profile.friends.add(friend2)

        # Make friendships mutual
        friend1.profile.friends.add(user)
        friend2.profile.friends.add(user)

    return users


def create_pending_friend_requests(num_requests=5):
    """
    Create users with pending friend requests between them.
    Useful for testing friend request features.
    """
    requests = []

    for i in range(num_requests):
        sender = User.objects.create_user(
            username=f"sender_{i}", email=f"sender{i}@test.com", password="testpass123"
        )

        receiver = User.objects.create_user(
            username=f"receiver_{i}",
            email=f"receiver{i}@test.com",
            password="testpass123",
        )

        # Create friend request
        friend_request = ProfileFriendRequest.objects.create(
            sender=sender.profile,
            receiver=receiver.profile,
            message=f"Hi! Let's connect and study together.",
        )

        requests.append(friend_request)

    return requests


def create_users_with_privacy_variations():
    """
    Create users with different privacy settings.
    Useful for testing privacy features.
    """
    privacy_configs = [
        {
            "username": "private_user",
            "search_visibility": "nobody",
            "profile_visibility": "private",
            "show_full_name": False,
            "show_email": False,
            "allow_friend_requests": False,
        },
        {
            "username": "public_user",
            "search_visibility": "everyone",
            "profile_visibility": "public",
            "show_full_name": True,
            "show_email": True,
            "allow_friend_requests": True,
        },
        {
            "username": "friends_only_user",
            "search_visibility": "friends_only",
            "profile_visibility": "friends_only",
            "show_full_name": True,
            "show_email": False,
            "allow_friend_requests": True,
        },
        {
            "username": "friends_of_friends_user",
            "search_visibility": "friends_of_friends",
            "profile_visibility": "friends_only",
            "show_full_name": True,
            "show_email": False,
            "allow_friend_requests": True,
        },
    ]

    users = []
    for config in privacy_configs:
        user = User.objects.create_user(
            username=config["username"],
            email=f"{config['username']}@test.com",
            password="testpass123",
        )

        # Apply privacy settings
        privacy = user.profile.privacy_settings
        privacy.search_visibility = config["search_visibility"]
        privacy.profile_visibility = config["profile_visibility"]
        privacy.show_full_name = config["show_full_name"]
        privacy.show_email = config["show_email"]
        privacy.allow_friend_requests = config["allow_friend_requests"]
        privacy.save()

        users.append(user)

    return users


def create_realistic_user_data(user, include_picture=False):
    """
    Fill user profile with realistic data based on their country.
    """
    # Country-specific data
    country_data = {
        "CA": {
            "cities": ["Toronto", "Montreal", "Vancouver", "Winnipeg", "Halifax"],
            "unis": ["UofT", "McGill", "UBC", "Concordia", "Dalhousie"],
            "langs": ["en", "fr"],
        },
        "NG": {
            "cities": ["Lagos", "Abuja", "Port Harcourt", "Kano", "Ibadan"],
            "unis": ["UI", "UNILAG", "ABU", "OAU", "FUTA"],
            "langs": ["en", "yo", "ig", "ha"],
        },
        "FR": {
            "cities": ["Paris", "Lyon", "Marseille", "Toulouse", "Lille"],
            "unis": ["Sorbonne", "Sciences Po", "École Polytechnique"],
            "langs": ["fr", "en", "ar"],
        },
        "BR": {
            "cities": ["São Paulo", "Rio", "Salvador", "Brasília", "Recife"],
            "unis": ["USP", "UFRJ", "UFMG", "UNICAMP"],
            "langs": ["pt", "es", "en"],
        },
    }

    # Add realistic bio
    if user.profile.country in country_data:
        data = country_data[user.profile.country]
        city = random.choice(data["cities"])

        if user.profile.occupation == "student":
            uni = random.choice(data["unis"])
            user.profile.bio = f"Student at {uni} in {city}. Passionate about making education accessible."
        else:
            user.profile.bio = f"Educator based in {city}. Committed to reaching underserved communities."

        # Set language if not set
        if not user.profile.preferred_language:
            user.profile.preferred_language = random.choice(data["langs"])

    user.profile.save()
    return user
