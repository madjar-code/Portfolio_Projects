from typing import Dict, Any
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from apps.auth.models import CustomUser


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Serializer for user registration.

    Extends Djoser's UserCreateSerializer to work with CustomUser model.
    """

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "email",
            "name",
            "password",
        )
        read_only_fields = ("id",)

    def validate_email(self, value: str) -> str:
        """
        Validate email uniqueness.
        
        Args:
            value: Email address to validate
            
        Returns:
            Validated email address
            
        Raises:
            ValidationError: If email already exists
        """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value.lower()


class CustomUserSerializer(UserSerializer):
    """
    Serializer for user data representation.
    
    Used for retrieving and updating user information.
    """
    
    is_email_user = serializers.SerializerMethodField()
    is_oauth_user = serializers.SerializerMethodField()
    
    class Meta(UserSerializer.Meta):
        model = CustomUser
        fields = (
            "id",
            "email",
            "name",
            "is_verified",
            "is_email_user",
            "is_oauth_user",
            "oauth_provider",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "email",
            "is_verified",
            "oauth_provider",
            "created_at",
            "updated_at",
        )
    
    def get_is_email_user(self, obj: CustomUser) -> bool:
        """Check if user registered via email/password."""
        return obj.is_email_user()
    
    def get_is_oauth_user(self, obj: CustomUser) -> bool:
        """Check if user registered via OAuth."""
        return obj.is_oauth_user()


class CustomUserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    """
    
    class Meta:
        model = CustomUser
        fields = ("name",)
    
    def update(self, instance: CustomUser, validated_data: Dict[str, Any]) -> CustomUser:
        """
        Update user instance.
        
        Args:
            instance: User instance to update
            validated_data: Validated data from request
            
        Returns:
            Updated user instance
        """
        instance.name = validated_data.get("name", instance.name)
        instance.save()
        return instance


class GoogleOAuthSerializer(serializers.Serializer):
    """
    Serializer for Google OAuth authentication.
    Accepts Google ID token from frontend.
    """
    token = serializers.CharField(
        required=True,
        help_text="Google ID token from frontend",
    )


class GoogleOAuthCodeSerializer(serializers.Serializer):
    """
    Serializer for Google OAuth code exchange.
    Accepts authorization code from Google OAuth flow.
    """
    code = serializers.CharField(
        required=True,
        help_text="Authorization code from Google OAuth",
    )
    redirect_uri = serializers.CharField(
        required=True,
        help_text="Redirect URI used in OAuth flow",
    )


class GoogleOAuthResponseSerializer(serializers.Serializer):
    """
    Serializer for Google OAuth response.
    Returns JWT tokens and user info.
    """
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = CustomUserSerializer(read_only=True)
    is_new_user = serializers.BooleanField(
        read_only=True,
        help_text="True if user was just created",
    )

