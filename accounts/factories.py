from django.contrib.auth.models import User

class UserFactory:
    @staticmethod
    def create_user(username, password, email=None, role="user"):
        user = User.objects.create_user(username=username, password=password, email=email)
        if role == "admin":
            user.is_staff = True
        user.save()
        return user