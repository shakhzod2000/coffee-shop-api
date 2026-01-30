"""
Coffee Shop API - Verification Service

Email/SMS verification code generation and validation.

NOTE: In a production environment, this would integrate with an email service
(e.g., SendGrid, AWS SES) or SMS provider (e.g., Twilio). For this demo,
verification codes are printed to the console.
"""

import random
import string


class VerificationService:
    """Service class for generating and handling verification codes."""
    
    @staticmethod
    def generate_code(length: int = 6) -> str:
        """Generate a random numeric verification code of the given length."""
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def send_verification_email(email: str, code: str) -> None:
        """
        Send a verification code to the user's email address.
        NOTE: This is a simplified implementation that prints to console.
        """
        print("=" * 50)
        print("VERIFICATION EMAIL (Console Output)")
        print("=" * 50)
        print(f"To: {email}")
        print(f"Subject: Verify your Coffee Shop account")
        print(f"")
        print(f"Your verification code is: {code}")
        print(f"")
        print(f"This code will expire in 24 hours.")
        print("=" * 50)
    
    @staticmethod
    def validate_code(stored_code: str | None, provided_code: str) -> bool:
        """Validate if the provided verification code matches the stored one."""
        if stored_code is None:
            return False
        return stored_code == provided_code
