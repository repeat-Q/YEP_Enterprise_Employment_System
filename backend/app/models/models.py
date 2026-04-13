from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text, ForeignKey, Float, Date, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

# ======== 枚举类型 ========
class UserRole(str, enum.Enum):
    enterprise = "enterprise"   # 企业端用户
    city = "city"               # 市级用户
    province = "province"       # 省级审批人员
    province_analyst = "province_analyst"  # 省级分析人员
    admin = "admin"             # 系统管理员

class ReportStatus(str, enum.Enum):
    draft = "draft"             # 草稿
    submitted = "submitted"     # 已提交
    city_review = "city_review" # 市级审核中
    city_approved = "city_approved"   # 市级已通过
    city_rejected = "city_rejected"   # 市级退回
    province_review = "province_review"  # 省级审批中
    province_approved = "province_approved"  # 省级已批准
    province_rejected = "province_rejected"  # 省级退回

class ReportPeriodType(str, enum.Enum):
    monthly = "monthly"         # 月度
    half_monthly = "half_monthly"  # 半月（1/2/3月使用）

# ======== 用户表 ========
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(50))
    role = Column(Enum(UserRole), nullable=False)
    enterprise_id = Column(Integer, ForeignKey("enterprises.id"), nullable=True)
    city_code = Column(String(20), nullable=True)   # 市级用户对应的城市编码
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    enterprise = relationship("Enterprise", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")

# ======== 企业表 ========
class Enterprise(Base):
    __tablename__ = "enterprises"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    credit_code = Column(String(50), unique=True, nullable=False, index=True)  # 统一社会信用代码
    city_code = Column(String(20), nullable=False)      # 所属城市
    district_code = Column(String(20))                  # 所属区县
    industry_code = Column(String(20))                  # 行业代码
    enterprise_type = Column(String(50))                # 企业类型
    registered_capital = Column(Float)                  # 注册资本（万元）
    address = Column(String(500))
    contact_name = Column(String(50))
    contact_phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    users = relationship("User", back_populates="enterprise")
    reports = relationship("EmploymentReport", back_populates="enterprise")

# ======== 就业失业数据采集报表 ========
class EmploymentReport(Base):
    __tablename__ = "employment_reports"
    id = Column(Integer, primary_key=True, index=True)
    enterprise_id = Column(Integer, ForeignKey("enterprises.id"), nullable=False)
    report_year = Column(Integer, nullable=False)       # 报告年份
    report_month = Column(Integer, nullable=False)      # 报告月份 1-12
    period_type = Column(Enum(ReportPeriodType), default=ReportPeriodType.monthly)
    half_period = Column(Integer, nullable=True)        # 半月期：1=上半月 2=下半月

    # 核心就业数据
    baseline_employed = Column(Integer, default=0)      # 建档期就业人数（基准值，BR-01）
    current_employed = Column(Integer, default=0)       # 当期在职人员数
    new_employed = Column(Integer, default=0)           # 新增就业人数
    lost_employed = Column(Integer, default=0)          # 减少就业人数（BR-01校验用）
    unemployed_count = Column(Integer, default=0)       # 失业人员数
    new_unemployed = Column(Integer, default=0)         # 新增失业人员数
    reemployed = Column(Integer, default=0)             # 再就业人数

    # 各类人员细分
    disabled_employed = Column(Integer, default=0)      # 残疾人就业
    veteran_employed = Column(Integer, default=0)       # 退役军人就业
    graduate_employed = Column(Integer, default=0)      # 应届毕业生就业
    poverty_employed = Column(Integer, default=0)       # 脱贫人口就业

    # 薪资数据
    avg_salary = Column(Float, default=0)               # 平均工资（元/月）
    total_salary = Column(Float, default=0)             # 工资总额（万元）

    # 流程状态
    status = Column(Enum(ReportStatus), default=ReportStatus.draft)
    submit_time = Column(DateTime, nullable=True)
    city_review_time = Column(DateTime, nullable=True)
    city_reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    city_review_comment = Column(Text, nullable=True)
    province_review_time = Column(DateTime, nullable=True)
    province_reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    province_review_comment = Column(Text, nullable=True)

    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    enterprise = relationship("Enterprise", back_populates="reports")

# ======== 审计日志 ========
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)        # 操作类型
    resource = Column(String(100))                      # 操作对象
    resource_id = Column(Integer, nullable=True)
    detail = Column(Text)                               # 操作详情
    ip_address = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="audit_logs")

# ======== 系统通知 ========
class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
