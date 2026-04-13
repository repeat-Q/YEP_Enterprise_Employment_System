from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.models import User, UserRole, Enterprise
from app.schemas.schemas import UserCreate, UserOut, EnterpriseCreate, EnterpriseOut
from app.services.auth_service import get_current_user, require_roles

router = APIRouter()

# ===== 用户管理 =====
@router.get("/users", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin))
):
    return db.query(User).all()

@router.post("/users", response_model=UserOut)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin))
):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=data.username,
        password_hash=get_password_hash(data.password),
        real_name=data.real_name,
        role=data.role,
        enterprise_id=data.enterprise_id,
        city_code=data.city_code
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.put("/users/{user_id}/toggle", response_model=UserOut)
def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user

# ===== 企业管理 =====
@router.get("/enterprises", response_model=List[EnterpriseOut])
def list_enterprises(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.province, UserRole.province_analyst))
):
    return db.query(Enterprise).filter(Enterprise.is_active == True).all()

@router.post("/enterprises", response_model=EnterpriseOut)
def create_enterprise(
    data: EnterpriseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin))
):
    if db.query(Enterprise).filter(Enterprise.credit_code == data.credit_code).first():
        raise HTTPException(status_code=400, detail="统一社会信用代码已存在")
    enterprise = Enterprise(**data.model_dump())
    db.add(enterprise)
    db.commit()
    db.refresh(enterprise)
    return enterprise

@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user
