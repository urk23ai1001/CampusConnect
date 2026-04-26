from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class RoleEnum(str, enum.Enum):
    manager = "manager"
    ambassador = "ambassador"

class TaskTypeEnum(str, enum.Enum):
    referral = "referral"
    content = "content"
    promotion = "promotion"
    custom = "custom"

class SubmissionStatusEnum(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class VoteTypeEnum(str, enum.Enum):
    up = "up"
    down = "down"

# ==================== USERS ====================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(Enum(RoleEnum), default=RoleEnum.ambassador)
    created_at = Column(DateTime, default=datetime.utcnow)

    organizations = relationship("Organization", back_populates="creator")
    ambassadors = relationship("Ambassador", back_populates="user")

# ==================== ORGANIZATIONS ====================
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    industry = Column(String)
    ambassador_capacity = Column(Integer, default=100)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="organizations")
    ambassadors = relationship("Ambassador", back_populates="organization")
    tasks = relationship("Task", back_populates="organization")

# ==================== AMBASSADORS ====================
class Ambassador(Base):
    __tablename__ = "ambassadors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    org_id = Column(Integer, ForeignKey("organizations.id"))
    points = Column(Integer, default=0)
    streak_count = Column(Integer, default=0)
    last_activity = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="ambassadors")
    organization = relationship("Organization", back_populates="ambassadors")
    submissions = relationship("Submission", back_populates="ambassador")
    votes = relationship("Vote", back_populates="ambassador")
    badges = relationship("AmbassadorBadge", back_populates="ambassador")

# ==================== TASKS ====================
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    title = Column(String, index=True)
    description = Column(Text)
    points = Column(Integer)
    deadline = Column(DateTime)
    task_type = Column(Enum(TaskTypeEnum), default=TaskTypeEnum.custom)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="tasks")
    submissions = relationship("Submission", back_populates="task")

# ==================== SUBMISSIONS ====================
class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    ambassador_id = Column(Integer, ForeignKey("ambassadors.id"))
    proof_url = Column(String)
    notes = Column(Text, nullable=True)
    status = Column(Enum(SubmissionStatusEnum), default=SubmissionStatusEnum.pending)
    score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="submissions")
    ambassador = relationship("Ambassador", back_populates="submissions")
    votes = relationship("Vote", back_populates="submission")

# ==================== BADGES ====================
class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, unique=True, index=True)
    name = Column(String)
    description = Column(Text)

    ambassadors = relationship("AmbassadorBadge", back_populates="badge")

class AmbassadorBadge(Base):
    __tablename__ = "ambassador_badges"

    id = Column(Integer, primary_key=True, index=True)
    ambassador_id = Column(Integer, ForeignKey("ambassadors.id"))
    badge_id = Column(Integer, ForeignKey("badges.id"))
    awarded_at = Column(DateTime, default=datetime.utcnow)

    ambassador = relationship("Ambassador", back_populates="badges")
    badge = relationship("Badge", back_populates="ambassadors")

# ==================== VOTES ====================
class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"))
    ambassador_id = Column(Integer, ForeignKey("ambassadors.id"))
    vote_type = Column(Enum(VoteTypeEnum))
    created_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("Submission", back_populates="votes")
    ambassador = relationship("Ambassador", back_populates="votes")

# ==================== LEADERBOARD CACHE ====================
class LeaderboardCache(Base):
    __tablename__ = "leaderboard_cache"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    ambassador_id = Column(Integer, ForeignKey("ambassadors.id"))
    rank = Column(Integer)
    total_points = Column(Integer)
    updated_at = Column(DateTime, default=datetime.utcnow)

# ==================== DUEL MODE 1v1 ====================
class DuelStatusEnum(str, enum.Enum):
    pending = "pending"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"

class Duel(Base):
    __tablename__ = "duels"

    id = Column(Integer, primary_key=True, index=True)
    challenger_id = Column(Integer, ForeignKey("ambassadors.id"))
    challenged_id = Column(Integer, ForeignKey("ambassadors.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))
    org_id = Column(Integer, ForeignKey("organizations.id"))
    challenger_score = Column(Integer, default=0)
    challenged_score = Column(Integer, default=0)
    winner_id = Column(Integer, ForeignKey("ambassadors.id"), nullable=True)
    status = Column(Enum(DuelStatusEnum), default=DuelStatusEnum.pending)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ==================== ACTIVITY HEATMAP ====================
class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    ambassador_id = Column(Integer, ForeignKey("ambassadors.id"))
    activity_type = Column(String)  # submission, vote, duel, login
    points = Column(Integer, default=0)
    date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
