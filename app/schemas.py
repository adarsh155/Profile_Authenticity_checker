from pydantic import BaseModel

class ProfileData(BaseModel):
    headline: str
    bio: str

class ProfileRequest(BaseModel):
    user_id: str
    profile_data: ProfileData

class HealthResponse(BaseModel):
    status: str

class VersionResponse(BaseModel):
    model_version: str
    model_type: str
