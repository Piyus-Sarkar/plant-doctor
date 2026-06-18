from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Plant(Base):
    __tablename__ = "plants"
    id = Column(Integer, primary_key=True, index=True)
    species = Column(String, index=True)
    location = Column(String)

class Photo(Base):
    __tablename__ = "photos"
    id = Column(Integer, primary_key=True, index=True)
    filepath = Column(String)
    plant_id = Column(Integer, ForeignKey("plants.id"))
    taken_at = Column(DateTime, default=datetime.datetime.utcnow)

class Diagnosis(Base):
    __tablename__ = "diagnoses"
    id = Column(Integer, primary_key=True, index=True)
    symptom_category = Column(String)
    description = Column(Text)
    health_score = Column(Integer, default=0)
    embedding = Column(Text, nullable=True) # NEW: Holds serialized vector float arrays
    plant_id = Column(Integer, ForeignKey("plants.id"))

class CareTask(Base):
    __tablename__ = "care_tasks"
    id = Column(Integer, primary_key=True, index=True)
    task_description = Column(String)
    is_completed = Column(Boolean, default=False)
    plant_id = Column(Integer, ForeignKey("plants.id"))