from sqlalchemy import Column, String, Float, Integer
from database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    gender = Column(String(20), nullable=False)
    gender_probability = Column(Float, nullable=False)
    sample_size = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)
    age_group = Column(String(20), nullable=False)
    country_id = Column(String(10), nullable=False)
    country_probability = Column(Float, nullable=False)
    created_at = Column(String(30), nullable=False)