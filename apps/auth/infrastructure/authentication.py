"""Custom authentication backends for API token validation."""

from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from apps.auth.infrastructure.orm_models import AuthToken


class BearerTokenAuthentication(TokenAuthentication):
    """
    Custom token authentication that validates custom Bearer tokens.
    
    Extends DRF's TokenAuthentication to work with our custom AuthToken model
    and enforces token expiration checking.
    
    Authorization header format: Authorization: Bearer <token>
    """
    
    keyword = 'Bearer'
    model = AuthToken
    
    def get_model(self):
        """Return the AuthToken model class."""
        if self.model is not None:
            return self.model
        return AuthToken
    
    def authenticate_credentials(self, key):
        """
        Authenticate the token key.
        
        Args:
            key: The token key from the Authorization header
            
        Returns:
            tuple: (user, token) if valid
            
        Raises:
            AuthenticationFailed: If token is invalid or expired
        """
        model = self.get_model()
        
        try:
            token = model.objects.select_related('user').get(access_token=key)
        except model.DoesNotExist:
            raise AuthenticationFailed('Invalid token.')
        
        # Check if token is marked as invalid
        if not token.is_valid:
            raise AuthenticationFailed('Token is invalid or revoked.')
        
        # Check if user is active
        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or deleted.')
        
        # Check if token has expired
        if token.expires_at and timezone.now() >= token.expires_at:
            raise AuthenticationFailed('Token has expired.')
        
        return (token.user, token)
