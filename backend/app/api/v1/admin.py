from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.models import User, UserRole, Enterprise, EmploymentReport, ReportStatus
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

# ===== 报表管理（管理员/省级）=====
@router.get("/reports", response_model=List[dict])
def admin_list_reports(
    page: int = 1,
    page_size: int = 20,
    enterprise_id: int = None,
    status: str = None,
    quarter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.province, UserRole.province_analyst))
):
    """管理员/省级查看所有报表"""
    q = db.query(EmploymentReport).join(Enterprise)
    if enterprise_id:
        q = q.filter(EmploymentReport.enterprise_id == enterprise_id)
    if status:
        q = q.filter(EmploymentReport.status == status)
    if quarter:
        q = q.filter(EmploymentReport.quarter == quarter)
    total = q.count()
    reports = q.order_by(EmploymentReport.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()
    return {"total": total, "items": reports}

@router.post("/reports", response_model=dict)
def admin_create_report(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin))
):
    """管理员创建报表"""
    report = EmploymentReport(**data)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

@router.put("/reports/{report_id}", response_model=dict)
def admin_update_report(
    report_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.enterprise))
):
    """更新报表"""
    report = db.query(EmploymentReport).filter(EmploymentReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报表不存在")
    for k, v in data.items():
        if hasattr(report, k) and k != 'id':
            setattr(report, k, v)
    db.commit()
    db.refresh(report)
    return report

@router.put("/reports/{report_id}/submit", response_model=dict)
def admin_submit_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.enterprise))
):
    """提交报表"""
    report = db.query(EmploymentReport).filter(EmploymentReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报表不存在")
    report.status = ReportStatus.city_review
    db.commit()
    db.refresh(report)
    return report

@router.put("/reports/{report_id}/reject", response_model=dict)
def admin_reject_report(
    report_id: int,
    reason: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.city, UserRole.province))
):
    """驳回报表"""
    report = db.query(EmploymentReport).filter(EmploymentReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报表不存在")
    if current_user.role == UserRole.city:
        report.status = ReportStatus.city_rejected
    else:
        report.status = ReportStatus.province_rejected
    db.commit()
    db.refresh(report)
    return report
