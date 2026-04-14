from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.models import User, UserRole, Enterprise, EmploymentReport, ReportStatus, ReportPeriodType
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

@router.put("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin))
):
    """更新用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if "real_name" in data and data["real_name"]:
        user.real_name = data["real_name"]
    if "role" in data and data["role"]:
        try:
            user.role = UserRole(data["role"])
        except ValueError:
            pass
    if "city_code" in data:
        user.city_code = data["city_code"]
    if "enterprise_id" in data:
        user.enterprise_id = data["enterprise_id"]
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

@router.put("/enterprises/{enterprise_id}", response_model=EnterpriseOut)
def update_enterprise(
    enterprise_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin))
):
    """更新企业信息"""
    enterprise = db.query(Enterprise).filter(Enterprise.id == enterprise_id).first()
    if not enterprise:
        raise HTTPException(status_code=404, detail="企业不存在")
    
    updatable_fields = ["name", "credit_code", "city_code", "district_code", 
                        "industry_code", "enterprise_type", "address", 
                        "contact_name", "contact_phone"]
    for field in updatable_fields:
        if field in data and data[field] is not None:
            setattr(enterprise, field, data[field])
    
    db.commit()
    db.refresh(enterprise)
    return enterprise

@router.delete("/enterprises/{enterprise_id}")
def delete_enterprise(
    enterprise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin))
):
    """删除企业（软删除）"""
    enterprise = db.query(Enterprise).filter(Enterprise.id == enterprise_id).first()
    if not enterprise:
        raise HTTPException(status_code=404, detail="企业不存在")
    
    # 检查是否有报表关联
    report_count = db.query(EmploymentReport).filter(
        EmploymentReport.enterprise_id == enterprise_id
    ).count()
    if report_count > 0:
        # 软删除
        enterprise.is_active = False
        db.commit()
        return {"message": "企业已停用（存在关联报表，已软删除）"}
    else:
        db.delete(enterprise)
        db.commit()
        return {"message": "企业已删除"}

@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user

# ===== 报表序列化辅助 =====
def serialize_report(r: EmploymentReport, enterprise_name: str = "") -> dict:
    """将ORM对象序列化为前端可用的字典"""
    return {
        "id": r.id,
        "enterprise_id": r.enterprise_id,
        "enterprise_name": enterprise_name,
        "report_year": r.report_year,
        "report_month": r.report_month,
        "period_type": r.period_type.value if r.period_type else "monthly",
        "half_period": r.half_period,
        "report_period": f"{r.report_year}年{r.report_month}月",
        "quarter": f"Q{(r.report_month - 1) // 3 + 1}",
        "baseline_employed": r.baseline_employed or 0,
        "current_employed": r.current_employed or 0,
        "new_employed": r.new_employed or 0,
        "lost_employed": r.lost_employed or 0,
        "unemployed_count": r.unemployed_count or 0,
        "new_unemployed": r.new_unemployed or 0,
        "reemployed": r.reemployed or 0,
        "disabled_employed": r.disabled_employed or 0,
        "veteran_employed": r.veteran_employed or 0,
        "graduate_employed": r.graduate_employed or 0,
        "poverty_employed": r.poverty_employed or 0,
        "avg_salary": r.avg_salary or 0,
        "total_salary": r.total_salary or 0,
        "status": r.status.value if r.status else "draft",
        "submit_time": r.submit_time.isoformat() if r.submit_time else None,
        "submitted_at": r.submit_time.isoformat() if r.submit_time else None,
        "city_review_comment": r.city_review_comment,
        "province_review_comment": r.province_review_comment,
        "remark": r.remark,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        # 前端兼容字段
        "employment_count": r.current_employed or 0,
        "unemployment_count": r.unemployed_count or 0,
        "employment_difficulty_count": r.poverty_employed or 0,
        "registered_unemployment_count": r.unemployed_count or 0,
    }

# ===== 报表管理（管理员/省级）=====
@router.get("/reports")
def admin_list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    enterprise_id: Optional[int] = None,
    status: Optional[str] = None,
    quarter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.province, UserRole.province_analyst))
):
    """管理员/省级查看所有报表"""
    q = db.query(EmploymentReport).join(Enterprise)
    if enterprise_id:
        q = q.filter(EmploymentReport.enterprise_id == enterprise_id)
    if status:
        try:
            status_enum = ReportStatus(status)
            q = q.filter(EmploymentReport.status == status_enum)
        except ValueError:
            pass  # 忽略无效状态值
    if quarter:
        # quarter格式: Q1/Q2/Q3/Q4 或 2026-Q1
        q_val = quarter.replace("2024-", "").replace("2025-", "").replace("2026-", "")
        month_map = {"Q1": [1, 2, 3], "Q2": [4, 5, 6], "Q3": [7, 8, 9], "Q4": [10, 11, 12]}
        if q_val in month_map:
            q = q.filter(EmploymentReport.report_month.in_(month_map[q_val]))
    
    total = q.count()
    reports = q.order_by(EmploymentReport.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    # 手动序列化
    items = []
    for r in reports:
        ent_name = r.enterprise.name if r.enterprise else ""
        items.append(serialize_report(r, ent_name))
    
    return {"total": total, "items": items}

@router.post("/reports")
def admin_create_report(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin))
):
    """管理员创建报表"""
    # 解析前端提交的数据
    report_year = data.get("report_year")
    report_month = data.get("report_month")
    
    # 从report_period解析年月 (格式: "2026-04")
    report_period = data.get("report_period", "")
    if report_period and "-" in report_period:
        parts = report_period.split("-")
        report_year = int(parts[0])
        report_month = int(parts[1])
    
    if not report_year or not report_month:
        raise HTTPException(status_code=400, detail="请选择报表周期")
    
    enterprise_id = data.get("enterprise_id")
    if not enterprise_id:
        raise HTTPException(status_code=400, detail="请选择企业")
    
    # 检查企业是否存在
    enterprise = db.query(Enterprise).filter(Enterprise.id == enterprise_id).first()
    if not enterprise:
        raise HTTPException(status_code=404, detail="企业不存在")
    
    report = EmploymentReport(
        enterprise_id=enterprise_id,
        report_year=report_year,
        report_month=report_month,
        period_type=ReportPeriodType.monthly,
        baseline_employed=data.get("baseline_employed", 0) or data.get("urban_employment", 0) or 0,
        current_employed=data.get("current_employed", 0) or data.get("urban_employment", 0) or 0,
        new_employed=data.get("new_employed", 0),
        lost_employed=data.get("lost_employed", 0),
        unemployed_count=data.get("unemployed_count", 0) or data.get("urban_unemployment", 0) or 0,
        new_unemployed=data.get("new_unemployed", 0),
        reemployed=data.get("reemployed", 0),
        disabled_employed=data.get("disabled_employed", 0),
        veteran_employed=data.get("veteran_employed", 0),
        graduate_employed=data.get("graduate_employed", 0),
        poverty_employed=data.get("poverty_employed", 0) or data.get("employment_difficulty", 0) or 0,
        avg_salary=data.get("avg_salary", 0),
        total_salary=data.get("total_salary", 0),
        remark=data.get("remark", ""),
        status=ReportStatus.draft
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return serialize_report(report, enterprise.name)

@router.put("/reports/{report_id}")
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
    
    # 更新字段
    field_map = {
        "baseline_employed": "baseline_employed",
        "current_employed": "current_employed",
        "urban_employment": "current_employed",  # 前端字段映射
        "new_employed": "new_employed",
        "lost_employed": "lost_employed",
        "unemployed_count": "unemployed_count",
        "urban_unemployment": "unemployed_count",  # 前端字段映射
        "new_unemployed": "new_unemployed",
        "reemployed": "reemployed",
        "disabled_employed": "disabled_employed",
        "veteran_employed": "veteran_employed",
        "graduate_employed": "graduate_employed",
        "poverty_employed": "poverty_employed",
        "employment_difficulty": "poverty_employed",  # 前端字段映射
        "avg_salary": "avg_salary",
        "total_salary": "total_salary",
        "remark": "remark",
        "employment_count": "current_employed",
        "unemployment_count": "unemployed_count",
    }
    
    for key, db_field in field_map.items():
        if key in data and data[key] is not None:
            setattr(report, db_field, data[key])
    
    db.commit()
    db.refresh(report)
    
    ent_name = report.enterprise.name if report.enterprise else ""
    return serialize_report(report, ent_name)

@router.put("/reports/{report_id}/submit")
def admin_submit_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.enterprise))
):
    """提交报表"""
    report = db.query(EmploymentReport).filter(EmploymentReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报表不存在")
    
    if report.status not in [ReportStatus.draft, ReportStatus.city_rejected, ReportStatus.province_rejected]:
        raise HTTPException(status_code=400, detail="报表状态不允许提交")
    
    report.status = ReportStatus.city_review
    report.submit_time = datetime.now()
    db.commit()
    db.refresh(report)
    
    ent_name = report.enterprise.name if report.enterprise else ""
    return serialize_report(report, ent_name)

@router.put("/reports/{report_id}/withdraw")
def admin_withdraw_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.enterprise))
):
    """撤回报表（变为草稿）"""
    report = db.query(EmploymentReport).filter(EmploymentReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报表不存在")
    
    if report.status not in [ReportStatus.city_review, ReportStatus.province_review]:
        raise HTTPException(status_code=400, detail="只有审核中的报表才能撤回")
    
    report.status = ReportStatus.draft
    report.submit_time = None
    db.commit()
    db.refresh(report)
    
    ent_name = report.enterprise.name if report.enterprise else ""
    return serialize_report(report, ent_name)

@router.put("/reports/{report_id}/reject")
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
        report.city_review_comment = reason
    else:
        report.status = ReportStatus.province_rejected
        report.province_review_comment = reason
    db.commit()
    db.refresh(report)
    
    ent_name = report.enterprise.name if report.enterprise else ""
    return serialize_report(report, ent_name)
