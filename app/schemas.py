from pydantic import BaseModel, EmailStr
from typing import Optional, List

class IdentifyRequest(BaseModel):
    email: Optional[EmailStr] = None
    phoneNumber: Optional[str] = None

class ContactDetail(BaseModel):
    primaryContactId: int  # Matching their spelling
    emails: List[str]
    phoneNumbers: List[str]
    secondaryContactIds: List[int]

class IdentifyResponse(BaseModel):
    contact: ContactDetail