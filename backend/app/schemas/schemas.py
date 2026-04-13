from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from app.models.models import UserRole, ReportStatus, ReportPeriodType

# ======== 认证 ========
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    real_name: str
    enterprise_id: Optional[int] = None

# ======== 用户 ========
class UserCreate(BaseModel):
    username: str
    password: str
    real_name: str
    role: UserRole
    enterprise_id: Optional[int] = None
    city_code: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    real_name: str
    role: str
    enterprise_id: Optional[int]
    city_code: Optional[str]
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

# ======== 企业 ========
class EnterpriseCreate(BaseModel):
    name: str
    credit_code: str
    city_code: str
    district_code: Optional[str] = None
    industry_code: Optional[str] = None
    enterprise_type: Optional[str] = None
    registered_capital: Optional[float] = None
    address: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None

class EnterpriseOut(BaseModel):
    id: int
    name: str
    credit_code: str
    city_code: str
    district_code: Optional[str]
    industry_code: Optional[str]
    enterprise_type: Optional[str]
    address: Optional[str]
    contact_name: Optional[str]
    contact_phone: Optional[str]
    is_active: bool
    class Config:
        from_attributes = True

# ======== 报表 ========
class ReportCreate(BaseModel):
    report_year: int
    report_month: int
    period_type: ReportPeriodType = ReportPeriodType.monthly
    half_period: Optional[int] = None

    baseline_employed: int = 0
    current_employed: int = 0
    new_employed: int = 0
    lost_employed: int = 0
    unemployed_count: int = 0
    new_unemployed: int = 0
    reemployed: int = 0

    disabled_employed: int = 0
    veteran_employed: int = 0
    graduate_employed: int = 0
    poverty_employed: int = 0

    avg_salary: float = 0
    total_salary: float = 0
    remark: Optional[str] = None

class ReportUpdate(BaseModel):
    baseline_employed: Optional[int] = None
    current_employed: Optional[int] = None
    new_employed: Optional[int] = None
    lost_employed: Optional[int] = None
    unemployed_count: Optional[int] = None
    new_unemployed: Optional[int] = None
    reemployed: Optional[int] = None
    disabled_employed: Optional[int] = None
    veteran_employed: Optional[int] = None
    graduate_employed: Optional[int] = None
    poverty_employed: Optional[int] = None
    avg_salary: Optional[float] = None
    total_salary: Optional[float] = None
    remark: Optional[str] = None

class ReportOut(BaseModel):
    id: int
    enterprise_id: int
    report_year: int
    report_month: int
    period_type: str
    half_period: Optional[int]
    baseline_employed: int
    current_employed: int
    new_employed: int
    lost_employed: int
    unemployed_count: int
    new_unemployed: int
    reemployed: int
    disabled_employed: int
    veteran_employed: int
    graduate_employed: int
    poverty_employed: int
    avg_salary: float
    total_salary: float
    status: str
    submit_time: Optional[datetime]
    city_review_comment: Optional[str]
    province_review_comment: Optional[str]
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class ReviewRequest(BaseModel):
    approve: bool
    comment: Optional[str] = None

# ======== 统计分析 ========
class StatsSummary(BaseModel):
    total_enterprises: int
    total_reports: int
    pending_city_review: int
    pending_province_review: int
    total_employed: int
    total_unemployed: int
