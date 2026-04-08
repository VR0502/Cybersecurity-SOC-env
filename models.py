from pydantic import BaseModel, Field
from enum import Enum
import uuid
from datetime import datetime

class ThreatType(str, Enum):
    BRUTE_FORCE = "brute_force"
    PHISHING = "phishing_email"
    MALWARE = "malware_execution"

class Observation(BaseModel):
    id: str
    srcIP: str
    typ: str   # threat type as string
    sev: int
    ts: str    # iso timestamp

class Action(BaseModel):
    code: int   # 0-4

class Reward(BaseModel):
    value: float
    info: dict = Field(default_factory=dict)

# Internal alert model (not exposed directly)
class Alert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    srcIP: str
    typ: ThreatType
    sev: int = Field(ge=1, le=10)
    ts: datetime = Field(default_factory=datetime.utcnow)