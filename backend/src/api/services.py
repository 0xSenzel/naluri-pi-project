import redis
from src.config import CIRCUMFERENCE_KEY, PI_KEY, SESSION_LIMIT, SUN_RADIUS_KM


class SessionManager:
    """Manages open SSE connection count per session ID."""
    def __init__(self):
        # {session_id: connection_count}
        self.active_sessions = {}

    def connect(self, session_id: str) -> bool:
        if self.active_sessions.get(session_id, 0) >= SESSION_LIMIT:
            return False # Throttled
        self.active_sessions[session_id] = self.active_sessions.get(session_id, 0) + 1
        return True

    def disconnect(self, session_id: str):
        if session_id in self.active_sessions:
            self.active_sessions[session_id] -= 1
            if self.active_sessions[session_id] <= 0:
                del self.active_sessions[session_id]

session_manager = SessionManager()

# Utility to read data from Redis
async def get_current_pi_data(r) -> dict:
    pi_value = await r.get(PI_KEY) or "3"
    circumference = await r.get(CIRCUMFERENCE_KEY) or str(2 * SUN_RADIUS_KM)
    return {"pi": pi_value, "circumference": circumference}