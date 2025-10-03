from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from accounts.factories import UserFactory

class AuthService:
    @staticmethod
    def signup(request, username, password1, password2):
        if password1 != password2:
            raise ValueError("Passwords do not match")

        try:
            user = UserFactory.create_user(username=username, password=password1)
            login(request, user)
            return user
        except IntegrityError:
            raise IntegrityError("Username already exists")

    @staticmethod
    def signin(request, username, password):
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
        return user

    @staticmethod
    def signout(request):
        logout(request)
