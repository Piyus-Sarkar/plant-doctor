from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- USER SCHEMAS ---
class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    
    class Config:
        from_attributes = True

# --- PLANT SCHEMAS ---
class PlantCreate(BaseModel):
    location: str
    # Species is optional because the AI might have to identify it for us!
    species: Optional[str] = None 

class PlantResponse(BaseModel):
    id: int
    species: Optional[str]
    location: str
    owner_id: int
    planted_at: datetime
    
    class Config:
        from_attributes = True

# --- PHOTO SCHEMAS ---
class PhotoResponse(BaseModel):
    id: int
    filepath: str
    plant_id: int
    taken_at: datetime
    
    class Config:
        from_attributes = True