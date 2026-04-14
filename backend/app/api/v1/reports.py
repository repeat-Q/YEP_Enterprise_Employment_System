from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models.models import User, UserRole, EmploymentReport, ReportStatus, AuditLog, Notification
from app.schemas.schemas import ReportCreate, ReportUpdate, ReportOut, ReviewRequest
from app.services.auth_service import get_current_user, require_roles
from app.services.br_validator import validate_report

router = APIRouter()

def log_action(db: Session, user_id: int, action: str, resource: str, resource_id: int = None, detail: str = "", ip: str = ""):
    log = AuditLog(user_id=user_id, action=action, resource=resource,
                   resource_id=resource_id, detail=detail, ip_address=ip)
    db.add(log)

def send_notification(db: Session, user_id: int, title: str, content: str):
    notif = Notification(user_id=user_id, title=title, content=content)
    db.add(notif)

# ===== 企业端 =====
@router.post("/reports", response_model=ReportOut)
def create_report(
    data: ReportCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.enterprise))
):
    """创建报表（草稿）"""
    # 检查是否已存在相同周期的报表
    q = db.query(EmploymentReport).filter(
        EmploymentReport.enterprise_id == current_user.enterprise_id,
        EmploymentReport.report_year == data.report_year,
        EmploymentReport.report_month == data.report_month,
        EmploymentReport.period_type == data.period_type
    )
    if data.half_period:
        q = q.filter(EmploymentReport.half_period == data.half_period)
    existing = q.first()
    if existing and existing.status not in [ReportStatus.draft, ReportStatus.city_rejected, ReportStatus.province_rejected]:
        raise HTTPException(status_code=400, detail="该周期报表已存在且处于审核流程中")

    report = EmploymentReport(enterprise_id=current_user.enterprise_id, **data.model_dump())
    db.add(report)
    db.flush()
    log_action(db, current_user.id, "创建报表", "employment_reports", report.id,
               f"年{data.report_year}月{data.report_month}", request.client.host if request.client else "")
    db.commit()
    db.refresh(report)
    return report

@router.put("/reports/{report_id}", response_model=ReportOut)
def update_report(
    report_id: int,
    data: ReportUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.enterprise))
):
    """更新报表（草稿状态）"""
    report = db.query(EmploymentReport).filter(
        EmploymentReport.id == report_id,
        EmploymentReport.enterprise_id == current_user.enterprise_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="报表不存在")
    if report.status not in [ReportStatus.draft, ReportStatus.city_rejected, ReportStatus.province_rejected]:
        raise HTTPException(status_code=400, detail="报表已提交，不能修改")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(report, field, value)
    log_action(db, current_user.id, "修改报表", "employment_reports", report_id, "", request.client.host if request.client else "")
    db.commit()
    db.refresh(report)
    return report

@router.post("/reports/{report_id}/submit", response_model=ReportOut)
def submit_report(
    report_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.enterprise))
):
    """提交报表（触发BR校验）"""
    report = db.query(EmploymentReport).filter(
        EmploymentReport.id == report_id,
        EmploymentReport.enterprise_id == current_user.enterprise_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="报表不存在")
    if report.status not in [ReportStatus.draft, ReportStatus.city_rejected, ReportStatus.province_rejected]:
        raise HTTPException(status_code=400, detail="报表已提交")

    # 构建校验数据
    report_data = ReportCreate(
        report_year=report.report_year,
        report_month=report.report_month,
        period_type=report.period_type,
        half_period=report.half_period,
        baseline_employed=report.baseline_employed,
        current_employed=report.current_employed,
        new_employed=report.new_employed,
        lost_employed=report.lost_employed,
        unemployed_count=report.unemployed_count,
        new_unemployed=report.new_unemployed,
        reemployed=report.reemployed,
        disabled_employed=report.disabled_employed,
        veteran_employed=report.veteran_employed,
        graduate_employed=report.graduate_employed,
        poverty_employed=report.poverty_employed,
        avg_salary=report.avg_salary,
        total_salary=report.total_salary
    )

    # BR红线校验
    errors = validate_report(report_data, existing_baseline=report.baseline_employed)
    # 排除BR-04（调查期限制），开发阶段不限制时间
    errors = [e for e in errors if e["rule"] != "BR-04"]
    if errors:
        raise HTTPException(status_code=422, detail={"br_errors": errors})

    report.status = ReportStatus.city_review
    report.submit_time = datetime.now()
    log_action(db, current_user.id, "提交报表", "employment_reports", report_id, "", request.client.host if request.client else "")
    db.commit()
    db.refresh(report)
    return report

@router.get("/reports", response_model=List[ReportOut])
def list_my_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.enterprise))
):
    """查看本企业所有报表"""
    return db.query(EmploymentReport).filter(
        EmploymentReport.enterprise_id == current_user.enterprise_id
    ).order_by(EmploymentReport.created_at.desc()).all()

@router.get("/reports/{report_id}", response_model=ReportOut)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report = db.query(EmploymentReport).filter(EmploymentReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报表不存在")
    # 企业端只能看自己的
    if current_user.role == UserRole.enterprise and report.enterprise_id != current_user.enterprise_id:
        raise HTTPException(status_code=403, detail="无权限访问此报表")
    return report

# ===== 市级端 =====
@router.get("/city/reports", response_model=List[ReportOut])
def list_city_reports(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.city))
):
    """市级查看辖区内待审核报表"""
    from app.models.models import Enterprise
    q = db.query(EmploymentReport).join(Enterprise).filter(
        Enterprise.city_code == current_user.city_code
    )
    if status_filter:
        q = q.filter(EmploymentReport.status == status_filter)
    else:
        q = q.filter(EmploymentReport.status == ReportStatus.city_review)
    return q.order_by(EmploymentReport.submit_time.desc()).all()

@router.post("/city/reports/{report_id}/review", response_model=ReportOut)
def city_review_report(
    report_id: int,
    data: ReviewRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.city))
):
    """市级审核报表"""
    report = db.query(EmploymentReport).filter(EmploymentReport.id == report_id).first()
    if not report or report.status != ReportStatus.city_review:
        raise HTTPException(status_code=400, detail="报表不存在或状态不正确")

    if data.approve:
        report.status = ReportStatus.province_review
    else:
        report.status = ReportStatus.city_rejected
    report.city_review_time = datetime.now()
    report.city_reviewer_id = current_user.id
    report.city_review_comment = data.comment

    log_action(db, current_user.id, "市级审核", "employment_reports", report_id,
               f"{'通过' if data.approve else '退回'}: {data.comment}", request.client.host if request.client else "")
    db.commit()
    db.refresh(report)
    return report

# ===== 省级端 =====
@router.get("/province/reports", response_model=List[ReportOut])
def list_province_reports(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.province, UserRole.province_analyst, UserRole.admin))
):
    """省级查看待审批报表"""
    q = db.query(EmploymentReport)
    if status_filter:
        q = q.filter(EmploymentReport.status == status_filter)
    else:
        q = q.filter(EmploymentReport.status == ReportStatus.province_review)
    return q.order_by(EmploymentReport.city_review_time.desc()).all()

@router.post("/province/reports/{report_id}/approve", response_model=ReportOut)
def province_approve_report(
    report_id: int,
    data: ReviewRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.province, UserRole.admin))
):
    """省级审批报表"""
    report = db.query(EmploymentReport).filter(EmploymentReport.id == report_id).first()
    if not report or report.status != ReportStatus.province_review:
        raise HTTPException(status_code=400, detail="报表不存在或状态不正确")

    if data.approve:
        report.status = ReportStatus.province_approved
    else:
        report.status = ReportStatus.province_rejected
    report.province_review_time = datetime.now()
    report.province_reviewer_id = current_user.id
    report.province_review_comment = data.comment

    log_action(db, current_user.id, "省级审批", "employment_reports", report_id,
               f"{'批准' if data.approve else '退回'}: {data.comment}", request.client.host if request.client else "")
    db.commit()
    db.refresh(report)
    return report

# ===== 统计分析 =====
@router.get("/stats/summary")
def get_stats_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """统计汇总数据"""
    from app.models.models import Enterprise
    from sqlalchemy import func

    total_enterprises = db.query(func.count(Enterprise.id)).scalar()
    total_reports = db.query(func.count(EmploymentReport.id)).scalar()
    pending_city = db.query(func.count(EmploymentReport.id)).filter(
        EmploymentReport.status == ReportStatus.city_review).scalar()
    pending_province = db.query(func.count(EmploymentReport.id)).filter(
        EmploymentReport.status == ReportStatus.province_review).scalar()
    approved_reports = db.query(EmploymentReport).filter(
        EmploymentReport.status == ReportStatus.province_approved).all()
    total_employed = sum(r.current_employed for r in approved_reports)
    total_unemployed = sum(r.unemployed_count for r in approved_reports)
    
    # 市级审核统计
    city_rejected = db.query(func.count(EmploymentReport.id)).filter(
        EmploymentReport.status == ReportStatus.city_rejected).scalar()
    
    # 今日已审核数（市级+省级）
    from sqlalchemy import cast, Date
    today = datetime.now().date()
    today_city_reviewed = db.query(func.count(EmploymentReport.id)).filter(
        cast(EmploymentReport.city_review_time, Date) == today
    ).scalar() if hasattr(EmploymentReport, 'city_review_time') else 0
    today_province_reviewed = db.query(func.count(EmploymentReport.id)).filter(
        cast(EmploymentReport.province_review_time, Date) == today
    ).scalar() if hasattr(EmploymentReport, 'province_review_time') else 0
    
    # 本月审核数
    month_start = today.replace(day=1)
    month_city_reviewed = db.query(func.count(EmploymentReport.id)).filter(
        EmploymentReport.city_review_time >= month_start
    ).scalar() if hasattr(EmploymentReport, 'city_review_time') else 0
    month_province_reviewed = db.query(func.count(EmploymentReport.id)).filter(
        EmploymentReport.province_review_time >= month_start
    ).scalar() if hasattr(EmploymentReport, 'province_review_time') else 0

    return {
        "total_enterprises": total_enterprises,
        "total_reports": total_reports,
        "pending_city_review": pending_city,
        "pending_province_review": pending_province,
        "total_employed": total_employed,
        "total_unemployed": total_unemployed,
        "approved_reports": len(approved_reports),
        "city_rejected": city_rejected,
        "today_city_reviewed": today_city_reviewed or 0,
        "today_province_reviewed": today_province_reviewed or 0,
        "month_city_reviewed": month_city_reviewed or 0,
        "month_province_reviewed": month_province_reviewed or 0,
    }

@router.get("/stats/trend")
def get_employment_trend(
    year: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """就业趋势数据（包含所有已提交的报表，不限于已批准）"""
    from datetime import datetime as dt
    from sqlalchemy import func

    if not year:
        year = dt.now().year

    # 查询所有已提交的报表（非草稿）
    from app.models.models import ReportStatus
    submitted_statuses = [
        ReportStatus.city_review, ReportStatus.city_approved,
        ReportStatus.province_review, ReportStatus.province_approved,
        ReportStatus.city_rejected, ReportStatus.province_rejected
    ]
    reports = db.query(EmploymentReport).filter(
        EmploymentReport.report_year == year,
        EmploymentReport.status.in_(submitted_statuses)
    ).order_by(EmploymentReport.report_month).all()

    trend = {}
    for r in reports:
        key = r.report_month
        if key not in trend:
            trend[key] = {"month": key, "employed": 0, "unemployed": 0, "new_employed": 0}
        trend[key]["employed"] += r.current_employed or 0
        trend[key]["unemployed"] += r.unemployed_count or 0
        trend[key]["new_employed"] += r.new_employed or 0

    # 排序
    result = sorted(trend.values(), key=lambda x: x["month"])
    return {"year": year, "trend": result}
