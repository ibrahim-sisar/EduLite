from django.core.management.base import BaseCommand
from EduLite.users.models import User
from EduLite.users.services.friend_suggestions import compute_friend_suggestions_for_user

class Command(BaseCommand):
    help = "Compute friend suggestions for all users"

    def handle(self, *args, **kwargs):
        for user in User.objects.all():
            compute_friend_suggestions_for_user(user)
        self.stdout.write(self.style.SUCCESS("Friend suggestions computed."))
