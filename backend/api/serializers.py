"""
User Serializers
Handles user registration and validation.
"""
from rest_framework import serializers
from django.contrib.auth.models import User


class UserRegistrationSerializer(serializers.Serializer):
    """
    Serializer for user registration.
    Validates username, email, and password.
    """
    username = serializers.CharField(
        min_length=3,
        max_length=150,
        help_text="Required. 3-150 characters."
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        help_text="Optional. Valid email address."
    )
    password = serializers.CharField(
        min_length=8,
        write_only=True,
        style={'input_type': 'password'},
        help_text="Required. Minimum 8 characters."
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Required. Must match password."
    )

    def validate_username(self, value):
        """Check if username is already taken."""
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value.lower()  # Store usernames in lowercase

    def validate_email(self, value):
        """Check if email is already registered (if provided)."""
        if value and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value.lower() if value else ""

    def validate(self, data):
        """Cross-field validation for password confirmation."""
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })
        return data

    def create(self, validated_data):
        """Create and return a new user."""
        # Remove confirm_password as it's not needed for user creation
        validated_data.pop('confirm_password')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user
