from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db import Base

class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # user_id = Column(Integer, ForeignKey('users.id'))  # Assuming you have a User model with id as a primary key

    # If you want to create a relationship with a User model
    # user = relationship("User", back_populates="chat_messages")
