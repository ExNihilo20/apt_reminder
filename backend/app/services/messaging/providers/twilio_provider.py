from twilio.rest import Client

from app.core.settings import get_settings
from app.services.messaging.providers.base import (
    BaseMessageProvider,
    MessageProviderError,
)


class TwilioProvider(BaseMessageProvider):
    def __init__(self):
        settings = get_settings()

        if not settings.twilio_account_sid or not settings.twilio_auth_token:
            raise MessageProviderError("Twilio credentials not configured")

        self.client = Client(
            settings.twilio_account_sid,
            settings.twilio_auth_token,
        )

        self.from_number = settings.twilio_from_number
        self.messaging_service_sid = settings.twilio_messaging_service_sid

    def send(self, *, to: str, body: str) -> dict:
        try:
            if self.messaging_service_sid:
                message = self.client.messages.create(
                    to=to,
                    body=body,
                    messaging_service_sid=self.messaging_service_sid,
                )
            else:
                message = self.client.messages.create(
                    to=to,
                    body=body,
                    from_=self.from_number,
                )

            return {
                "provider": "twilio",
                "provider_message_sid": message.sid,
                "status": message.status,
            }

        except Exception as e:
            raise MessageProviderError(str(e))