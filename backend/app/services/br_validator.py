"""
BR红线规则校验服务
实现15条业务规则校验，防止非法数据进入系统
"""
from typing import Optional
from datetime import datetime, date
from app.schemas.schemas import ReportCreate

class BRValidationError(Exception):
    def __init__(self, rule: str, message: str):
        self.rule = rule
        self.message = message
        super().__init__(f"[{rule}] {message}")

def get_survey_period(year: int, month: int, half_period: Optional[int] = None):
    """获取调查期范围"""
    if month in [1, 2, 3] and half_period:
        if half_period == 1:
            return date(year, month, 1), date(year, month, 15)
        else:
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            return date(year, month, 16), date(year, month, last_day)
    else:
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        return date(year, month, 1), date(year, month, last_day)

def validate_report(data: ReportCreate, existing_baseline: Optional[int] = None) -> list:
    """
    执行所有BR红线校验
    返回：校验通过返回[]，失败返回错误列表
    """
    errors = []

    # BR-01: 动态减员校验 — 减少就业人数不能超过建档期就业基准值
    baseline = existing_baseline if existing_baseline is not None else data.baseline_employed
    if baseline > 0 and data.lost_employed > baseline:
        errors.append({
            "rule": "BR-01",
            "message": f"减少就业人数({data.lost_employed})超过建档期就业基准值({baseline})，请核实数据"
        })

    # BR-02: 在职人数一致性 — 当期在职 = 上期在职 + 新增 - 减少（简化：新增≥减少时在职≥0）
    if data.current_employed < 0:
        errors.append({"rule": "BR-02", "message": "当期在职人数不能为负数"})

    # BR-03: 失业人数合理性 — 失业人数不超过在职人数
    if data.unemployed_count > data.current_employed and data.current_employed > 0:
        errors.append({
            "rule": "BR-03",
            "message": f"失业人数({data.unemployed_count})不能超过当期在职人数({data.current_employed})"
        })

    # BR-04: 调查期外操作拦截 — 检查当前时间是否在调查期内
    today = date.today()
    start, end = get_survey_period(data.report_year, data.report_month, data.half_period)
    # 允许在调查期结束后7天内补录
    from datetime import timedelta
    allowed_end = end + timedelta(days=7)
    if today < start or today > allowed_end:
        errors.append({
            "rule": "BR-04",
            "message": f"当前日期({today})不在调查期({start}至{end}+7天缓冲)内，无法提交填报"
        })

    # BR-05: 平均工资合理性 — 不低于当地最低工资标准（云南省2026年约2070元）
    MIN_SALARY = 2070
    if data.avg_salary > 0 and data.avg_salary < MIN_SALARY:
        errors.append({
            "rule": "BR-05",
            "message": f"平均工资({data.avg_salary}元)低于云南省最低工资标准({MIN_SALARY}元)，请核实"
        })

    # BR-06: 特殊群体人数合理性 — 残疾人/退役军人等不超过总在职人数
    special_total = (data.disabled_employed + data.veteran_employed +
                     data.graduate_employed + data.poverty_employed)
    if data.current_employed > 0 and special_total > data.current_employed:
        errors.append({
            "rule": "BR-06",
            "message": f"特殊群体就业总数({special_total})超过当期在职人数({data.current_employed})"
        })

    # BR-07: 新增就业人数非负
    if data.new_employed < 0:
        errors.append({"rule": "BR-07", "message": "新增就业人数不能为负数"})

    # BR-08: 新增失业人数非负
    if data.new_unemployed < 0:
        errors.append({"rule": "BR-08", "message": "新增失业人数不能为负数"})

    # BR-09: 再就业人数不超过失业人数
    if data.reemployed > data.unemployed_count and data.unemployed_count > 0:
        errors.append({
            "rule": "BR-09",
            "message": f"再就业人数({data.reemployed})不能超过失业人数({data.unemployed_count})"
        })

    # BR-10: 半月触发模式校验 — 1/2/3月必须指定half_period
    if data.report_month in [1, 2, 3] and data.period_type == "half_monthly":
        if data.half_period not in [1, 2]:
            errors.append({
                "rule": "BR-10",
                "message": "1/2/3月半月触发模式必须指定上半月(1)或下半月(2)"
            })

    # BR-11: 工资总额合理性 — 工资总额与平均工资和人数基本匹配
    if data.avg_salary > 0 and data.current_employed > 0 and data.total_salary > 0:
        expected_total = data.avg_salary * data.current_employed / 10000  # 转为万元
        if abs(data.total_salary - expected_total) / expected_total > 0.5:
            errors.append({
                "rule": "BR-11",
                "message": f"工资总额({data.total_salary}万元)与平均工资×人数({expected_total:.2f}万元)差异超过50%，请核实"
            })

    # BR-12: 年份合理性
    current_year = datetime.now().year
    if data.report_year < 2020 or data.report_year > current_year + 1:
        errors.append({"rule": "BR-12", "message": f"报告年份({data.report_year})不合理"})

    # BR-13: 月份合理性
    if data.report_month < 1 or data.report_month > 12:
        errors.append({"rule": "BR-13", "message": f"报告月份({data.report_month})不合理，应为1-12"})

    # BR-14: 减少就业人数非负
    if data.lost_employed < 0:
        errors.append({"rule": "BR-14", "message": "减少就业人数不能为负数"})

    # BR-15: 建档期就业基准值非负
    if data.baseline_employed < 0:
        errors.append({"rule": "BR-15", "message": "建档期就业基准值不能为负数"})

    return errors
