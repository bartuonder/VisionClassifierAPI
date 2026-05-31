from db.database import Base
from sqlalchemy import Column,Integer, String,Boolean, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class Users(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique = True, index=True)
    hashed_password = Column(String)
    tasks = relationship("ImageTask", back_populates="owner")


class ImageTask(Base):

    __tablename__ = "image_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String, nullable=False)
    status = Column(String, default="pending")
    prediction_label = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    owner = relationship("Users", back_populates="tasks")