from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Enum as SqlEnum
from sqlalchemy.sql import func
from database.database import Base
import enum

class ChannelType(str, enum.Enum):
    MANDATORY = "mandatory"
    REWARD = "reward"

class User(Base):
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    referred_by = Column(BigInteger, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Channel(Base):
    __tablename__ = "channels"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(BigInteger, nullable=False, unique=True)
    username = Column(String(255), nullable=True)
    title = Column(String(255), nullable=False)
    invite_link = Column(String(512), nullable=False)
    channel_type = Column(SqlEnum(ChannelType), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RewardLink(Base):
    __tablename__ = "reward_links"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(64), unique=True, nullable=False, index=True)
    channel_id = Column(Integer, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used = Column(Boolean, default=False)
    used_at = Column(DateTime(timezone=True), nullable=True)

class AdminLog(Base):
    __tablename__ = "admin_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(BigInteger, nullable=False)
    action = Column(String(512), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())