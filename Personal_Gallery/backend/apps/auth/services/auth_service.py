"""
Authentication service for handling user authentication logic.
"""
from typing import Dict, Tuple
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

from apps.auth.models import CustomUser
from .google_oauth import GoogleOAuthService


class AuthService:
    """
    Service for handling authentication business logic.
    """

    @staticmethod
    def authenticate_with_google_token(token: str) -> Dict:
        """
        Authenticate user with Google ID token.

        Args:
            token: Google ID token from frontend

        Returns:
            Dictionary with access, refresh tokens, user data, and is_new_user flag

        Raises:
            ValueError: If token is invalid or authentication fails
        """
        # Verify token and get user info (raises ValueError if invalid)
        user_info = GoogleOAuthService.verify_google_token(token)

        # Get or create user
        user, created = AuthService._get_or_create_oauth_user(
            email=user_info["email"],
            name=user_info["name"],
            oauth_provider="google",
            oauth_id=user_info["google_id"],
            is_verified=user_info["is_verified"],
        )

        # Generate JWT tokens
        tokens = AuthService._generate_tokens_for_user(user)

        return {
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "user": user,
            "is_new_user": created,
        }

    @staticmethod
    def authenticate_with_google_code(code: str, redirect_uri: str) -> Dict:
        """
        Authenticate user with Google authorization code.

        Args:
            code: Authorization code from Google OAuth flow
            redirect_uri: Redirect URI used in OAuth flow

        Returns:
            Dictionary with access, refresh tokens, user data, and is_new_user flag

        Raises:
            ValueError: If code exchange fails or authentication fails
        """
        # Exchange code for token and get user info
        _, user_info = GoogleOAuthService.exchange_code_for_token(
            code, redirect_uri,
        )

        # Get or create user
        user, created = AuthService._get_or_create_oauth_user(
            email=user_info["email"],
            name=user_info.get("name", ""),
            oauth_provider="google",
            oauth_id=user_info["id"],  # Google API returns "id", not "google_id"
            is_verified=user_info.get("verified_email", False),
        )

        # Generate JWT tokens
        tokens = AuthService._generate_tokens_for_user(user)

        return {
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "user": user,
            "is_new_user": created,
        }

    @staticmethod
    @transaction.atomic
    def _get_or_create_oauth_user(
        email: str,
        name: str,
        oauth_provider: str,
        oauth_id: str,
        is_verified: bool,
    ) -> Tuple[CustomUser, bool]:
        # Try to get existing user by email
        try:
            user = CustomUser.objects.get(email=email)
            created = False

            # If user exists but wasn't OAuth user, update OAuth info
            if not user.oauth_provider:
                user.oauth_provider = oauth_provider
                user.oauth_id = oauth_id
                user.is_verified = True
                user.save()

        except CustomUser.DoesNotExist:
            # Create new user
            user = CustomUser.objects.create(
                email=email,
                name=name,
                oauth_provider=oauth_provider,
                oauth_id=oauth_id,
                is_verified=is_verified,
            )
            created = True

        return user, created

    @staticmethod
    def _generate_tokens_for_user(user: CustomUser) -> Dict[str, str]:
        """
        Generate JWT tokens for user.

        Args:
            user: User instance

        Returns:
            Dictionary with accecss and refresh tokens
        """
        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
