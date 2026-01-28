"""
Custom email templates for authentication.
"""
from djoser import email


class ActivationEmail(email.ActivationEmail):
    """
    Email sent to user for account activation.
    """
    template_name = "auth/activation.html"


class ConfirmationEmail(email.ConfirmationEmail):
    """
    Email sent to user after successful registration.
    """
    template_name = "auth/confirmation.html"


class PasswordResetEmail(email.PasswordResetEmail):
    """
    Email sent to user for password reset.
    """
    template_name = "auth/password_reset.html"
