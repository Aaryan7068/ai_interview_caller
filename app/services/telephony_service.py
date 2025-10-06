from twilio.rest import Client
from app.core.config import settings
from typing import Optional

class TelephonyService:
    def __init__(self, account_sid: str, auth_token: str, from_number: str, base_url: str):
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number
        self.base_url = base_url

    def trigger_outbound_call(self, to_number: str, candidate_id: str) -> Optional[str]:
        initial_url = f"{self.base_url}/twilio/interview/start/{candidate_id}"

        try:
            call = self.client.calls.create(
                to=to_number,
                from_=self.from_number,
                url=initial_url,
                method='POST',
                timeout=30
            )
            return call.sid
        except Exception as e:
            print(f"Twilio Call Initiation Error: {e}")
            return None