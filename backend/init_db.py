# -*- coding: utf-8 -*-
"""
初始化数据库测试数据
"""
import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine
from app.core.database import Base
from app.core.security import get_password_hash
from app.models.models import User, UserRole, Enterprise

def init_db():
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 检查是否已初始化
        if db.query(User).count() > 0:
            print("数据库已初始化，跳过")
            return

        # 创建企业
        enterprises = [
            Enterprise(name="云南昆明科技有限公司", credit_code="91530100MA6ABCD123",
                      city_code="530100", district_code="530102",
                      industry_code="I65", enterprise_type="有限责任公司",
                      address="昆明市五华区科技路1号", contact_name="张三", contact_phone="13812345678"),
            Enterprise(name="云南大理旅游开发股份公司", credit_code="91532900MA6EFGH456",
                      city_code="532900", district_code="532901",
                      industry_code="N77", enterprise_type="股份有限公司",
                      address="大理市古城区民族路88号", contact_name="李四", contact_phone="13987654321"),
            Enterprise(name="曲靖市鑫源矿业集团", credit_code="91530300MA6IJKL789",
                      city_code="530300", district_code="530302",
                      industry_code="B06", enterprise_type="有限责任公司",
                      address="曲靖市麒麟区工业园区", contact_name="王五", contact_phone="13765432109"),
        ]
        for e in enterprises:
            db.add(e)
        db.flush()

        # 创建用户
        users = [
            User(username="admin", password_hash=get_password_hash("admin123"),
                 real_name="系统管理员", role=UserRole.admin),
            User(username="enterprise1", password_hash=get_password_hash("ent123456"),
                 real_name="张三", role=UserRole.enterprise, enterprise_id=enterprises[0].id),
            User(username="enterprise2", password_hash=get_password_hash("ent123456"),
                 real_name="李四", role=UserRole.enterprise, enterprise_id=enterprises[1].id),
            User(username="enterprise3", password_hash=get_password_hash("ent123456"),
                 real_name="王五", role=UserRole.enterprise, enterprise_id=enterprises[2].id),
            User(username="city_km", password_hash=get_password_hash("city123456"),
                 real_name="昆明市人社局-赵审核", role=UserRole.city, city_code="530100"),
            User(username="city_dali", password_hash=get_password_hash("city123456"),
                 real_name="大理州人社局-钱审核", role=UserRole.city, city_code="532900"),
            User(username="city_qj", password_hash=get_password_hash("city123456"),
                 real_name="曲靖市人社局-孙审核", role=UserRole.city, city_code="530300"),
            User(username="province", password_hash=get_password_hash("prov123456"),
                 real_name="云南省人社厅-审批官", role=UserRole.province),
            User(username="analyst", password_hash=get_password_hash("analyst123"),
                 real_name="省级数据分析员", role=UserRole.province_analyst),
        ]
        for u in users:
            db.add(u)

        db.commit()
        print("✓ 数据库初始化完成！")
        print("\n测试账号：")
        print("  管理员:    admin / admin123")
        print("  企业端:    enterprise1 / ent123456  (昆明科技公司)")
        print("  企业端:    enterprise2 / ent123456  (大理旅游公司)")
        print("  市级审核:  city_km / city123456     (昆明市)")
        print("  省级审批:  province / prov123456")
        print("  数据分析:  analyst / analyst123")

    except Exception as e:
        db.rollback()
        print(f"✗ 初始化失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
