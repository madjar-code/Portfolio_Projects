"""
API views for authentication.
"""
import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema

from apps.auth.services import AuthService
from .serializers import (
    GoogleOAuthSerializer,
    GoogleOAuthCodeSerializer,
    GoogleOAuthResponseSerializer,
)

logger = logging.getLogger(__name__)


class GoogleOAuthView(APIView):
    """
    Google OAuth authentication endpoint.
    
    Accepts Google ID token from frontend and returns JWT tokens.
    Creates new user if doesn't exist.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Authenticate with Google OAuth using ID token",
        request_body=GoogleOAuthSerializer,
        responses={
            200: GoogleOAuthResponseSerializer,
            400: "Bad Request - Invalid token",
            500: "Internal Server Error",
        },
        tags=["Authentication"],
    )
    def post(self, request):
        """
        Authenticate user with Google ID token.
        """
        # Validate input
        serializer = GoogleOAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data["token"]
        
        try:
            # Call service to handle authentication
            result = AuthService.authenticate_with_google_token(token)
            
            # Serialize response
            response_serializer = GoogleOAuthResponseSerializer({
                "access": result["access"],
                "refresh": result["refresh"],
                "user": result["user"],
                "is_new_user": result["is_new_user"],
            })
            
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.warning(f"Google OAuth validation error: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception(f"Google OAuth authentication failed: {str(e)}")
            return Response(
                {"detail": f"Authentication failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GoogleOAuthCodeView(APIView):
    """
    Google OAuth code exchange endpoint.
    
    Accepts authorization code from Google OAuth flow and returns JWT tokens.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Exchange Google OAuth code for JWT tokens",
        request_body=GoogleOAuthCodeSerializer,
        responses={
            200: GoogleOAuthResponseSerializer,
            400: "Bad Request - Invalid code",
            500: "Internal Server Error",
        },
        tags=["Authentication"],
    )
    def post(self, request):
        """
        Exchange Google authorization code for JWT tokens.
        """
        # Validate input
        serializer = GoogleOAuthCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data["code"]
        redirect_uri = serializer.validated_data["redirect_uri"]
        
        try:
            # Call service to handle authentication
            result = AuthService.authenticate_with_google_code(code, redirect_uri)
            
            # Serialize response
            response_serializer = GoogleOAuthResponseSerializer({
                "access": result["access"],
                "refresh": result["refresh"],
                "user": result["user"],
                "is_new_user": result["is_new_user"],
            })
            
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.warning(f"Google OAuth code exchange validation error: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception(f"Google OAuth code exchange failed: {str(e)}")
            return Response(
                {"detail": f"Authentication failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
