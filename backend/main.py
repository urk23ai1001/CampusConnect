import os
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import engine, get_db
from models import Base, User, Organization, Ambassador, Task, Submission, Badge, AmbassadorBadge, Vote
from schemas import *
from auth import hash_password, verify_password, create_access_token, get_current_user
from services import predict_rankings, get_task_recommendations, generate_org_insights

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CampusConnect API",
    description="Dual-sided Ambassador Management Platform",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== AUTH ROUTES ====================
@app.post("/auth/signup", response_model=UserResponse)
def signup(request: UserSignupRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = hash_password(request.password)
    user = User(email=request.email, password_hash=hashed_pwd, role=request.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/auth/login")
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """Login user and return JWT token."""
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(
        data={"sub": user.id, "role": user.role},
        expires_delta=timedelta(days=7)
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    }

@app.get("/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current authenticated user."""
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ==================== ORGANIZATION ROUTES ====================
@app.post("/organizations", response_model=OrganizationResponse)
def create_organization(
    request: OrganizationCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manager creates a new organization."""
    if current_user["role"] != "manager":
        raise HTTPException(status_code=403, detail="Only managers can create organizations")
    
    org = Organization(
        name=request.name,
        industry=request.industry,
        ambassador_capacity=request.ambassador_capacity,
        created_by=current_user["user_id"]
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

@app.get("/organizations", response_model=list[OrganizationResponse])
def list_organizations(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List organizations managed by current user."""
    orgs = db.query(Organization).filter(Organization.created_by == current_user["user_id"]).all()
    return orgs

@app.get("/organizations/{org_id}", response_model=OrganizationResponse)
def get_organization(org_id: int, db: Session = Depends(get_db)):
    """Get organization details."""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

# ==================== TASK ROUTES ====================
@app.post("/tasks", response_model=TaskResponse)
def create_task(
    request: TaskCreate,
    org_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manager creates a task."""
    if current_user["role"] != "manager":
        raise HTTPException(status_code=403, detail="Only managers can create tasks")
    
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    if org.created_by != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your organization")
    
    task = Task(
        org_id=org_id,
        title=request.title,
        description=request.description,
        points=request.points,
        deadline=request.deadline,
        task_type=request.task_type,
        created_by=current_user["user_id"]
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(org_id: int, db: Session = Depends(get_db)):
    """List tasks for an organization."""
    tasks = db.query(Task).filter(Task.org_id == org_id).all()
    return tasks

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get task details."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# ==================== SUBMISSION ROUTES ====================
@app.post("/submissions", response_model=SubmissionResponse)
def create_submission(
    request: SubmissionCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ambassador submits proof for a task."""
    # Find ambassador record
    ambassador = db.query(Ambassador).filter(Ambassador.user_id == current_user["user_id"]).first()
    if not ambassador:
        raise HTTPException(status_code=404, detail="Ambassador not found")
    
    task = db.query(Task).filter(Task.id == request.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    submission = Submission(
        task_id=request.task_id,
        ambassador_id=ambassador.id,
        proof_url=request.proof_url,
        notes=request.notes,
        status="pending"
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission

@app.get("/submissions", response_model=list[SubmissionResponse])
def list_submissions(
    org_id: int,
    status: str = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manager views submissions for their organization."""
    query = db.query(Submission).join(Task).filter(Task.org_id == org_id)
    if status:
        query = query.filter(Submission.status == status)
    return query.all()

@app.post("/submissions/{submission_id}/approve")
def approve_submission(
    submission_id: int,
    score: int = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manager approves a submission."""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    task = db.query(Task).filter(Task.id == submission.task_id).first()
    if task.created_by != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your task")
    
    # Auto-score logic
    final_score = score if score else task.points
    submission.status = "approved"
    submission.score = final_score
    
    # Update ambassador points
    ambassador = submission.ambassador
    ambassador.points += final_score
    
    # Update last activity for streak
    from datetime import datetime
    ambassador.last_activity = datetime.utcnow()
    
    db.commit()
    db.refresh(submission)
    
    return {
        "status": "ok",
        "submission_id": submission.id,
        "new_score": final_score,
        "ambassador_total_points": ambassador.points
    }

@app.post("/submissions/{submission_id}/reject")
def reject_submission(
    submission_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manager rejects a submission."""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    task = db.query(Task).filter(Task.id == submission.task_id).first()
    if task.created_by != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your task")
    
    submission.status = "rejected"
    db.commit()
    return {"status": "ok", "submission_id": submission.id}

# ==================== LEADERBOARD ROUTES ====================
@app.get("/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard(org_id: int, db: Session = Depends(get_db)):
    """Get real-time leaderboard for organization."""
    from sqlalchemy import func
    
    # Query approved submissions, group by ambassador, sum points
    leaderboard_data = db.query(
        Ambassador.id,
        func.sum(Submission.score).label("total_points"),
        Ambassador.streak_count,
        func.row_number().over(
            order_by=func.sum(Submission.score).desc()
        ).label("rank")
    ).join(Submission).filter(
        Ambassador.org_id == org_id,
        Submission.status == "approved"
    ).group_by(Ambassador.id).all()
    
    entries = []
    for rank, (ambassador_id, total_points, streak_count, _) in enumerate(leaderboard_data, 1):
        ambassador = db.query(Ambassador).filter(Ambassador.id == ambassador_id).first()
        user = db.query(User).filter(User.id == ambassador.user_id).first()
        badges = db.query(Badge).join(AmbassadorBadge).filter(
            AmbassadorBadge.ambassador_id == ambassador_id
        ).all()
        
        entries.append({
            "rank": rank,
            "ambassador_id": ambassador_id,
            "ambassador_name": user.email.split("@")[0],
            "total_points": total_points or 0,
            "streak_count": streak_count,
            "badges": [b.name for b in badges]
        })
    
    from datetime import datetime
    return {
        "entries": entries,
        "updated_at": datetime.utcnow()
    }

# ==================== AI PREDICTION ROUTES ====================
@app.get("/leaderboard/predictions", response_model=list[PredictionResponse])
def get_predictions(org_id: int, db: Session = Depends(get_db)):
    """Get AI predictions for next week's rankings."""
    # Fetch current rankings and historical data
    ambassadors = db.query(Ambassador).filter(Ambassador.org_id == org_id).all()
    
    current_rankings = []
    historical_data = []
    streak_info = []
    
    for amb in ambassadors:
        user = db.query(User).filter(User.id == amb.user_id).first()
        current_rankings.append({
            "ambassador_id": amb.id,
            "name": user.email,
            "current_points": amb.points
        })
        streak_info.append({
            "ambassador_id": amb.id,
            "streak": amb.streak_count
        })
    
    # Call AI service
    org_data = {
        "current_rankings": current_rankings,
        "historical_data": historical_data,
        "streak_info": streak_info,
        "org_name": "org"
    }
    
    predictions_result = predict_rankings(org_data)
    
    return predictions_result.get("predictions", [])

@app.get("/organizations/{org_id}/insights")
def get_org_insights(
    org_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI insights for organization manager."""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org or org.created_by != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your organization")
    
    ambassadors = db.query(Ambassador).filter(Ambassador.org_id == org_id).all()
    org_data = {
        "org_name": org.name,
        "ambassador_count": len(ambassadors),
        "ambassadors": [{"id": a.id, "points": a.points} for a in ambassadors]
    }
    
    insights = generate_org_insights(org_data)
    return insights

# ==================== VOTE ROUTES ====================
@app.post("/votes")
def create_vote(
    request: VoteCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ambassador votes on a submission."""
    ambassador = db.query(Ambassador).filter(Ambassador.user_id == current_user["user_id"]).first()
    if not ambassador:
        raise HTTPException(status_code=404, detail="Ambassador not found")
    
    # Check if already voted
    existing_vote = db.query(Vote).filter(
        Vote.submission_id == request.submission_id,
        Vote.ambassador_id == ambassador.id
    ).first()
    if existing_vote:
        raise HTTPException(status_code=400, detail="Already voted")
    
    vote = Vote(
        submission_id=request.submission_id,
        ambassador_id=ambassador.id,
        vote_type=request.vote_type
    )
    db.add(vote)
    db.commit()
    db.refresh(vote)
    return vote

@app.get("/submissions/{submission_id}/votes")
def get_submission_votes(submission_id: int, db: Session = Depends(get_db)):
    """Get vote count for submission."""
    upvotes = db.query(Vote).filter(
        Vote.submission_id == submission_id,
        Vote.vote_type == "up"
    ).count()
    downvotes = db.query(Vote).filter(
        Vote.submission_id == submission_id,
        Vote.vote_type == "down"
    ).count()
    return {
        "submission_id": submission_id,
        "upvotes": upvotes,
        "downvotes": downvotes,
        "net_votes": upvotes - downvotes
    }

# ==================== HEALTH CHECK ====================
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "CampusConnect API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
