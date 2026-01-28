"""
Google OAuth service for authentication.
"""
from typing import Dict, Optional, Tuple
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests
import requests as http_requests


class GoogleOAuthService:
    """
    Service for handling Google OAuth authentication.
    """

    @staticmethod
    def verify_google_token(token: str) -> Dict:
        """
        Verify Google OAuth token and extract user information.

        Args:
            token: Google ID token from frontend

        Returns:
            Dictionary with user info (email, name, google_id)

        Raises:
            ValueError: If token is invalid or missing required fields
        """
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_OAUTH_CLIENT_ID
            )

            # Verify the issuer
            if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
                raise ValueError("Wrong issuer.")

            # Validate required fields
            email = idinfo.get("email")
            google_id = idinfo.get("sub")

            if not email or not google_id:
                raise ValueError("Missing required fields in token")

            # Extract user information
            user_info = {
                "email": email,
                "name": idinfo.get("name", ""),
                "google_id": google_id,
                "is_verified": idinfo.get("email_verified", False),
            }

            return user_info

        except ValueError as e:
            raise ValueError(f"Invalid token: {str(e)}")
        except Exception as e:
            raise ValueError(f"Token verification failed: {str(e)}")

    @staticmethod
    def exchange_code_for_token(code: str, redirect_uri: str) -> Tuple[str, Dict]:
        """
        Exchange authorization code for access token and user info.

        Args:
            code: Authorization code from Google
            redirect_uri: Redirect URI used in the OAuth flow

        Returns:
            Tuple of (access_token, user_info)

        Raises:
            ValueError: If code exchange fails
        """
        token_url = "https://oauth2.googleapis.com/token"

        data = {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        try:
            # Exchange code for token
            response = http_requests.post(token_url, data=data)
            response.raise_for_status()
            token_data = response.json()

            # Get user info using access token
            userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            userinfo_response = http_requests.get(userinfo_url, headers=headers)
            userinfo_response.raise_for_status()
            user_info = userinfo_response.json()

            return token_data["access_token"], user_info

        except http_requests.RequestException as e:
            raise ValueError(f"Failed to exchange code: {str(e)}")
