"""Auth API views."""
from uuid import UUID

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.auth.application.use_cases.register import RegisterUseCase, RegisterCommand
from apps.auth.application.use_cases.login import LoginUseCase, LoginCommand
from apps.auth.application.use_cases.logout import LogoutUseCase, LogoutCommand
from apps.auth.infrastructure.repositories import DjangoUserRepository, DjangoTokenRepository
from apps.auth.infrastructure.password_service import PasswordService
from apps.auth.interfaces.api.serializers import (
    RegisterSerializer,
    LoginSerializer,
    LoginResponseSerializer,
    LogoutSerializer,
    RefreshTokenSerializer,
    RefreshTokenResponseSerializer,
)
from infrastructure.database.unit_of_work import UnitOfWork
from infrastructure.audit.audit_logger import AuditLogger
from shared.domain.exceptions import EntityNotFound, InvalidOperation

# Initialize audit logger instance
audit_logger = AuditLogger()


class RegisterView(APIView):
    """API endpoint for user registration."""
    
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"
    
    def post(self, request):
        """Register new user."""
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Initialize repositories and services
        user_repo = DjangoUserRepository()
        password_service = PasswordService()
        unit_of_work = UnitOfWork()
        
        # Execute use case
        use_case = RegisterUseCase(
            user_repo=user_repo,
            password_service=password_service,
            unit_of_work=unit_of_work,
        )
        
        command = RegisterCommand(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            full_name=serializer.validated_data["full_name"],
        )
        
        try:
            result = use_case.execute(command)
        except (EntityNotFound, InvalidOperation) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        
        # Log action
        audit_logger.log(
            actor_id="system",
            actor_role="system",
            action="USER_REGISTERED",
            entity_type="user",
            entity_id=result["user_id"],
            detail={"email": result["email"]},
        )
        
        return Response(result, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """API endpoint for user login."""
    
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"
    
    def post(self, request):
        """Login user and return tokens."""
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Initialize repositories and services
        user_repo = DjangoUserRepository()
        token_repo = DjangoTokenRepository()
        password_service = PasswordService()
        unit_of_work = UnitOfWork()
        
        # Execute use case
        use_case = LoginUseCase(
            user_repo=user_repo,
            token_repo=token_repo,
            password_service=password_service,
            unit_of_work=unit_of_work,
        )
        
        command = LoginCommand(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        
        try:
            result = use_case.execute(command)
        except (EntityNotFound, InvalidOperation) as exc:
            audit_logger.log(
                actor_id="anonymous",
                actor_role="anonymous",
                action="LOGIN_FAILED",
                entity_type="user",
                entity_id=serializer.validated_data["email"],
                detail={"email": serializer.validated_data["email"], "reason": str(exc)},
                ip_address=request.META.get("REMOTE_ADDR"),
                outcome="failure",
            )
            return Response({"detail": str(exc)}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Log action
        audit_logger.log(
            actor_id=str(result["user_id"]),
            actor_role="user",
            action="LOGIN",
            entity_type="user",
            entity_id=result["user_id"],
            detail={"email": result["email"]},
        )
        
        # Return response
        response_serializer = LoginResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """API endpoint for user logout."""
    
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"
    
    def post(self, request):
        """Logout user and revoke tokens."""
        # Get user_id from request (set by authentication middleware)
        user_id = getattr(request.user, 'user_id', None)
        if not user_id:
            # For now, we can extract from token if available
            access_token = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
            if not access_token:
                return Response(
                    {"error": "Unauthorized"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            access_token = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        
        # Initialize repositories
        token_repo = DjangoTokenRepository()
        user_repo = DjangoUserRepository()
        unit_of_work = UnitOfWork()
        
        # Get token to get user_id
        token = token_repo.get_by_access_token(access_token)
        if not token:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Execute use case
        use_case = LogoutUseCase(
            token_repo=token_repo,
            user_repo=user_repo,
            unit_of_work=unit_of_work,
        )
        
        command = LogoutCommand(
            user_id=token.user_id,
            access_token=access_token,
        )
        
        result = use_case.execute(command)
        
        # Log action
        audit_logger.log(
            actor_id=str(token.user_id),
            actor_role="user",
            action="LOGOUT",
            entity_type="user",
            entity_id=str(token.user_id),
        )
        
        response_serializer = LogoutSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class RefreshTokenView(APIView):
    """API endpoint for token refresh."""
    
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"
    
    def post(self, request):
        """Refresh access token using refresh token."""
        import secrets
        from datetime import timedelta
        from django.utils import timezone
        
        serializer = RefreshTokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        refresh_token = serializer.validated_data.get('refresh_token')
        
        # Initialize repository
        token_repo = DjangoTokenRepository()
        
        # Get token by refresh_token
        token = token_repo.get_by_refresh_token(refresh_token)
        if not token:
            return Response(
                {'detail': 'Invalid refresh token.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if refresh token is expired
        if token.expires_at and timezone.now() > token.expires_at:
            return Response(
                {'detail': 'Refresh token expired.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate new access token
        new_access_token = secrets.token_urlsafe(32)
        expires_in = 3600  # 1 hour
        
        # Update token with new access_token and expiration
        token.access_token = new_access_token
        token.expires_at = timezone.now() + timedelta(seconds=expires_in)
        token_repo.update(token)
        
        # Log action
        audit_logger.log(
            actor_id=str(token.user_id),
            actor_role="user",
            action="TOKEN_REFRESH",
            entity_type="user",
            entity_id=str(token.user_id),
        )
        
        # Return response
        response_data = {
            'access_token': new_access_token,
            'token_type': 'Bearer',
            'expires_in': expires_in
        }
        response_serializer = RefreshTokenResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
