"""Auth serializers for request/response validation."""
from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    """Serializer for user registration."""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(max_length=255)
    
    def validate_password(self, value):
        """Validate password strength."""
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError("Password must contain at least one digit")
        return value


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class LoginResponseSerializer(serializers.Serializer):
    """Serializer for login response."""
    
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    token_type = serializers.CharField()
    expires_in = serializers.IntegerField()
    user_id = serializers.CharField()
    email = serializers.EmailField()
    full_name = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout."""
    
    status = serializers.CharField()
    message = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    """Serializer for token refresh endpoint."""
    
    refresh_token = serializers.CharField()


class RefreshTokenResponseSerializer(serializers.Serializer):
    """Serializer for token refresh response."""
    
    access_token = serializers.CharField()
    token_type = serializers.CharField()
    expires_in = serializers.IntegerField()
