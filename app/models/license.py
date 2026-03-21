from pydantic import BaseModel
from typing import List


class LicensePayload(BaseModel):
    license_key: str
    status: str
    device_id: str
    issued_at: int
    expires_at: int
    features: List[str]


class LicenseResponse(BaseModel):
    payload: LicensePayload
    signature: str