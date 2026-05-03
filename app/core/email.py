import logging
from typing import Optional
from supabase import create_client, Client

from app.core.config import get_settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None
    ):
        settings = get_settings()
        self.url = supabase_url or settings.supabase_url
        self.key = supabase_key or settings.supabase_service_role_key
        self._supabase: Optional[Client] = None
        
        if self.url and self.key:
            try:
                self._supabase = create_client(self.url, self.key)
                logger.info("Supabase Email Client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client for email: {str(e)}")

    async def send_welcome_email(self, to_email: str):
        """
        Triggers the 'Confirm Your Signup' email template in Supabase.
        """
        if not self._supabase:
            logger.warning(f"Email sending skipped for {to_email}: SUPABASE_SERVICE_ROLE_KEY missing.")
            print(f"--- SIMULATED SUPABASE EMAIL TO {to_email} ---")
            print("Action: Triggering 'signup' (Confirm Your Signup) template.")
            print("--- END SIMULATION ---")
            return

        try:
            # Using resend to trigger the 'signup' confirmation template
            # In Supabase, 'signup' type triggers the 'Confirm Your Signup' template seen in your dashboard.
            response = self._supabase.auth.resend({
                "type": "signup",
                "email": to_email,
                "options": {
                    "redirectTo": "http://localhost:5173/auth/callback"
                }
            })
            
            logger.info(f"Supabase welcome email (Confirm Signup) triggered for {to_email}")
            return response
        except Exception as e:
            logger.error(f"Failed to trigger Supabase email for {to_email}: {str(e)}")
            return None
