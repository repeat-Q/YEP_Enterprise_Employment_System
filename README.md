# 云南省企业就业失业数据采集系统

企业就业失业数据采集系统 V1.0 | Vue3 + FastAPI + MySQL

## 系统架构

```
前端 (Vue3 + Vite)  -->  后端 (FastAPI)  -->  数据库 (MySQL)
  http://127.0.0.1:8000     http://127.0.0.1:8000     localhost:3306
  (静态文件由后端服务)    (API + 前端统一端口)
```

## 快速启动

### 方式一：一键启动（推荐）
双击运行 `start_all.bat` 即可启动完整系统（前后端共用8000端口）。

### 方式二：手动启动
```bash
cd backend
python start_server.py
```
访问 http://127.0.0.1:8000 即可使用系统。

## 访问地址

| 服务 | 地址 |
|------|------|
| 前端页面 | http://127.0.0.1:8000 |
| 后端API | http://127.0.0.1:8000 |
| API文档 | http://127.0.0.1:8000/docs |
| 数据库 | localhost:3306 (yep_employment) |

## 测试账号

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 系统管理员 | admin | admin123 | 全权限，含市级审核+省级审批 |
| 数据分析 | analyst | analyst123 | 省级分析师 |
| 省级审批 | province | prov123456 | 省级审批官 |
| 市级审核 | city_km | city123456 | 昆明市 |
| 市级审核 | city_dali | city123456 | 大理州 |
| 市级审核 | city_qj | city123456 | 曲靖市 |
| 企业端 | enterprise1 | ent123456 | 云南昆明科技 |
| 企业端 | enterprise2 | ent123456 | 云南大理旅游 |
| 企业端 | enterprise3 | ent123456 | 曲靖鑫源矿业 |
| 企业端 | testuser | ent123456 | 测试用户 |

## 功能模块

- **企业端**：报表填写、提交、查看状态
- **市级端**：审核下辖企业报表
- **省级端**：审批全省报表、数据分析
- **系统管理**：用户管理、企业管理

## 技术栈

- **前端**：Vue3 + Vite + Element Plus + ECharts + Pinia
- **后端**：FastAPI + SQLAlchemy + JWT
- **数据库**：MySQL 8.4

## 项目结构

```
YEP_Enterprise_Employment_System/
├── backend/
│   ├── app/
│   │   ├── api/v1/      # API路由
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 数据模型
│   │   ├── schemas/     # Pydantic模型
│   │   ├── services/    # 业务逻辑
│   │   └── main.py      # 入口文件
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/       # 页面组件
│   │   ├── stores/      # 状态管理
│   │   ├── router/      # 路由配置
│   │   └── utils/       # 工具函数
│   ├── dist/            # 编译产物
│   └── package.json
└── start_all.bat        # 一键启动脚本
```

## 数据表

- `users` - 用户表
- `enterprises` - 企业表
- `employment_reports` - 就业报表
- `audit_logs` - 审计日志
- `notifications` - 通知表

## 报表审核流程

```
企业创建 --> 企业提交 --> 市级审核 --> 省级审批 --> 完成
  (草稿)   (待审核)    (待审批)    (已批准)
              ↓           ↓
           (退回)      (退回)
              ↓           ↓
           (修改)      (修改)
```

## BR红线校验

系统对提交的报表进行业务规则校验：
- BR-01: 期末人数 = 期初 + 新增 - 流失
- BR-02: 新增人数范围校验
- BR-03: 失业人数合理性校验
- BR-05: 平均工资合理性校验