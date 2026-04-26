from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum

# ==================== ENUMS ====================
class RoleEnum(str, Enum):
    manager = "manager"
    ambassador = "ambassador"

class TaskTypeEnum(str, Enum):
    referral = "referral"
    content = "content"
    promotion = "promotion"
    custom = "custom"

class SubmissionStatusEnum(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class VoteTypeEnum(str, Enum):
    up = "up"
    down = "down"

# ==================== AUTH SCHEMAS ====================
class UserSignupRequest(BaseModel):
    email: EmailStr
    password: str
    role: RoleEnum

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: RoleEnum
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== ORGANIZATION SCHEMAS ====================
class OrganizationCreate(BaseModel):
    name: str
    industry: str
    ambassador_capacity: Optional[int] = 100

class OrganizationResponse(BaseModel):
    id: int
    name: str
    industry: str
    ambassador_capacity: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== AMBASSADOR SCHEMAS ====================
class AmbassadorCreate(BaseModel):
    user_id: int
    org_id: int

class AmbassadorResponse(BaseModel):
    id: int
    user_id: int
    org_id: int
    points: int
    streak_count: int
    last_activity: Optional[datetime]

    class Config:
        from_attributes = True

# ==================== TASK SCHEMAS ====================
class TaskCreate(BaseModel):
    title: str
    description: str
    points: int
    deadline: datetime
    task_type: TaskTypeEnum

class TaskResponse(BaseModel):
    id: int
    org_id: int
    title: str
    description: str
    points: int
    deadline: datetime
    task_type: TaskTypeEnum
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== SUBMISSION SCHEMAS ====================
class SubmissionCreate(BaseModel):
    task_id: int
    proof_url: str
    notes: Optional[str] = None

class SubmissionResponse(BaseModel):
    id: int
    task_id: int
    ambassador_id: int
    proof_url: str
    status: SubmissionStatusEnum
    score: int
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== BADGE SCHEMAS ====================
class BadgeResponse(BaseModel):
    id: int
    type: str
    name: str
    description: str

    class Config:
        from_attributes = True

class AmbassadorBadgeResponse(BaseModel):
    ambassador_id: int
    badge_id: int
    awarded_at: datetime

    class Config:
        from_attributes = True

# ==================== VOTE SCHEMAS ====================
class VoteCreate(BaseModel):
    submission_id: int
    vote_type: VoteTypeEnum

class VoteResponse(BaseModel):
    id: int
    submission_id: int
    ambassador_id: int
    vote_type: VoteTypeEnum
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== LEADERBOARD SCHEMAS ====================
class LeaderboardEntry(BaseModel):
    rank: int
    ambassador_id: int
    ambassador_name: str
    total_points: int
    streak_count: int
    badges: List[str]

class LeaderboardResponse(BaseModel):
    entries: List[LeaderboardEntry]
    updated_at: datetime

class PredictionResponse(BaseModel):
    ambassador_id: int
    predicted_rank: int
    confidence: float
    reasoning: str
