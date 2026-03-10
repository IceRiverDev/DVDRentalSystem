# 🎬 DVDRental API

基于 **FastAPI + SQLAlchemy 2.x（异步）** 构建的生产级 DVD 租赁系统后端服务，完整覆盖 PostgreSQL `dvdrental` 示例数据库的全部 15 张业务表。

---

## 📋 目录

- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [数据库 ER 关系](#数据库-er-关系)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [API 接口总览](#api-接口总览)
- [核心设计](#核心设计)
- [运行测试](#运行测试)

---

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | ≥ 0.115 | Web 框架，自动生成 OpenAPI 文档 |
| SQLAlchemy | ≥ 2.0 | 异步 ORM，`mapped_column` 声明式模型 |
| asyncpg | ≥ 0.30 | PostgreSQL 异步驱动 |
| Pydantic v2 | ≥ 2.10 | 数据校验与序列化 |
| pydantic-settings | ≥ 2.7 | 环境变量配置管理 |
| Uvicorn | ≥ 0.34 | ASGI 服务器 |
| Alembic | ≥ 1.14 | 数据库迁移 |
| pytest-asyncio | ≥ 0.25 | 异步测试套件 |

---

## 项目结构

```
DVDRentalSystem/
├── app/
│   ├── main.py                    # 应用入口：lifespan、中间件、路由注册
│   ├── core/
│   │   ├── config.py              # pydantic-settings 配置，读取 .env
│   │   └── database.py            # 异步 engine、session factory、DBSession 依赖
│   ├── models/
│   │   └── models.py              # SQLAlchemy 2.x ORM 模型（全 15 张表）
│   ├── schemas/
│   │   ├── base.py                # PagedResponse[T] 泛型基础模型
│   │   ├── geography.py           # Country / City / Address
│   │   ├── catalog.py             # Language / Category / Actor
│   │   ├── film.py                # Film / FilmDetail（含嵌套关联）
│   │   ├── people.py              # Customer / Staff / Store
│   │   └── transactions.py        # Inventory / Rental / Payment
│   ├── services/
│   │   ├── base.py                # 泛型 CRUD BaseService[T]
│   │   ├── actor_service.py       # 演员搜索、关联影片查询
│   │   ├── film_service.py        # 多条件搜索、管理演员/分类
│   │   ├── customer_service.py    # 客户搜索、租借历史
│   │   ├── rental_service.py      # 租借/归还业务（含冲突检查）
│   │   └── inventory_service.py   # 可用库存查询
│   ├── api/
│   │   ├── deps.py                # 分页参数依赖注入
│   │   └── v1/
│   │       ├── router.py          # v1 路由聚合
│   │       ├── actors.py          # 演员 CRUD + 关联影片
│   │       ├── films.py           # 影片 CRUD + 演员/分类管理
│   │       ├── customers.py       # 客户 CRUD + 租借历史
│   │       ├── rentals.py         # 租借 CRUD + 归还 + 逾期查询
│   │       ├── payments.py        # 支付 CRUD + 收入统计
│   │       ├── inventory.py       # 库存 CRUD + 可用查询
│   │       └── reference.py       # 参考数据：分类/语言/国家/城市/员工/门店
│   └── exceptions/
│       └── handlers.py            # 统一异常处理（409 / 404 / 500）
├── tests/
│   ├── conftest.py                # session 级异步客户端 fixture
│   └── test_api.py                # 15 个端到端 API 测试
├── .env                           # 本地环境配置（不提交到版本控制）
├── .env.example                   # 配置模板
├── requirements.txt
└── pyproject.toml                 # pytest 配置
```

---

## 数据库 ER 关系

```
country ──< city ──< address ──< customer ──< rental ──< payment
                          │                       │
                          ├──< staff ─────────────┘
                          └──< store
                                 │
actor ──< film_actor >──── film ──< inventory ──< rental
category ──< film_category >─┘
language ──────────────────┘
```

---

## 快速开始

### 1. 克隆并安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填写数据库连接信息
```

### 3. 启动服务

```bash
# 开发模式（热重载）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. 查看 API 文档

启动后访问：

| 地址 | 说明 |
|------|------|
| http://localhost:8000/docs | Swagger UI（交互式） |
| http://localhost:8000/redoc | ReDoc（阅读友好） |
| http://localhost:8000/health | 健康检查接口 |

---

## 配置说明

所有配置项通过 `.env` 文件注入，支持环境变量覆盖：

```ini
# 数据库连接
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=dvdrental

# 应用配置
API_V1_PREFIX=/api/v1
PROJECT_NAME=DVDRental API
DEBUG=false                        # true 时开启 SQL 日志

# CORS 白名单（JSON 数组格式）
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8080"]
```

---

## API 接口总览

所有接口前缀为 `/api/v1`，支持 JSON 请求/响应。

### 🎭 演员 `/actors`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/actors` | 列表，支持 `?name=` 搜索、分页 |
| POST | `/actors` | 创建演员 |
| GET | `/actors/{id}` | 获取详情 |
| PATCH | `/actors/{id}` | 更新演员 |
| DELETE | `/actors/{id}` | 删除演员 |
| GET | `/actors/{id}/films` | 该演员参演的所有影片 |

### 🎬 影片 `/films`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/films` | 列表，支持 `?title=` `?rating=` `?language_id=` `?category_id=` 过滤 |
| POST | `/films` | 创建影片 |
| GET | `/films/{id}` | 获取详情（含演员、分类、语言） |
| PATCH | `/films/{id}` | 更新影片 |
| DELETE | `/films/{id}` | 删除影片 |
| POST | `/films/{id}/actors/{actor_id}` | 为影片添加演员 |
| DELETE | `/films/{id}/actors/{actor_id}` | 移除演员 |
| POST | `/films/{id}/categories/{category_id}` | 为影片添加分类 |

### 👥 客户 `/customers`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/customers` | 列表，支持 `?name=` `?email=` `?active=` 过滤 |
| POST | `/customers` | 创建客户 |
| GET | `/customers/{id}` | 获取详情（含地址） |
| PATCH | `/customers/{id}` | 更新客户 |
| DELETE | `/customers/{id}` | 删除客户 |
| GET | `/customers/{id}/rentals` | 客户租借历史（分页） |

### 📦 库存 `/inventory`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/inventory` | 列表，支持 `?store_id=` 过滤 |
| POST | `/inventory` | 新增库存 |
| GET | `/inventory/available` | 查询可借库存，`?film_id=` `?store_id=` |
| GET | `/inventory/{id}` | 获取单条 |
| PATCH | `/inventory/{id}` | 更新 |
| DELETE | `/inventory/{id}` | 删除 |

### 🤝 租借 `/rentals`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/rentals` | 列表（按日期降序） |
| POST | `/rentals` | 创建租借（自动检查库存是否已借出） |
| GET | `/rentals/overdue` | 逾期未还列表 |
| GET | `/rentals/{id}` | 获取详情 |
| POST | `/rentals/{id}/return` | 归还（可指定归还时间） |
| PATCH | `/rentals/{id}` | 更新 |
| DELETE | `/rentals/{id}` | 删除 |

### 💳 支付 `/payments`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/payments` | 列表，支持 `?customer_id=` 过滤 |
| POST | `/payments` | 创建支付记录 |
| GET | `/payments/summary` | 收入汇总（总笔数、总金额、均值） |
| GET | `/payments/{id}` | 获取详情 |
| PATCH | `/payments/{id}` | 更新 |
| DELETE | `/payments/{id}` | 删除 |

### 📚 参考数据

| 路径 | 说明 |
|------|------|
| `GET /categories` | 所有影片分类 |
| `POST /categories` | 创建分类 |
| `PATCH /categories/{id}` | 更新分类 |
| `DELETE /categories/{id}` | 删除分类 |
| `GET /languages` | 所有语言 |
| `POST /languages` | 创建语言 |
| `PATCH /languages/{id}` | 更新语言 |
| `GET /countries` | 所有国家 |
| `GET /countries/{id}` | 国家详情 |
| `GET /cities` | 城市列表，支持 `?country_id=` 过滤 |
| `GET /staff` | 员工列表 |
| `GET /staff/{id}` | 员工详情 |
| `PATCH /staff/{id}` | 更新员工 |
| `GET /stores` | 门店列表 |
| `GET /stores/{id}` | 门店详情（含经理、地址） |

---

## 分页

所有列表接口均支持统一分页参数：

```
GET /api/v1/films?page=2&size=10
```

响应格式：

```json
{
  "items": [...],
  "total": 1000,
  "page": 2,
  "size": 10,
  "pages": 100
}
```

---

## 核心设计

### 异步分层架构

```
HTTP 请求
    │
    ▼
Router (FastAPI)       — 路由、参数校验、HTTP 语义
    │  Depends(DBSession)
    ▼
Service (业务层)        — 业务规则、事务、复杂查询
    │  AsyncSession
    ▼
SQLAlchemy ORM         — 异步 SQL 生成与执行
    │
    ▼
asyncpg → PostgreSQL
```

### 泛型 BaseService

所有资源继承 `BaseService[ModelT]`，获得通用 CRUD 能力：

```python
class FilmService(BaseService[Film]):
    model = Film

    async def search(self, title: str | None, ...): ...
    async def add_actor(self, film_id: int, actor_id: int): ...
```

### 依赖注入

通过 `Annotated` + `Depends` 注入异步会话，路由函数无需手动管理事务：

```python
DBSession = Annotated[AsyncSession, Depends(get_db)]

@router.get("/{film_id}")
async def get_film(film_id: int, db: DBSession):
    ...
```

### 统一异常处理

| 异常类型 | HTTP 状态码 | 说明 |
|---------|------------|------|
| `HTTPException(404)` | 404 | 资源不存在 |
| `HTTPException(409)` | 409 | 业务冲突（重复租借等） |
| `IntegrityError` | 409 | 数据库约束冲突 |
| 其他未处理异常 | 500 | 内部错误（不泄露详情） |

---

## 运行测试

```bash
# 运行全部测试
pytest tests/ -v

# 运行单个测试
pytest tests/test_api.py::test_get_film_detail -v

# 带覆盖率报告
pytest tests/ --cov=app --cov-report=term-missing
```

测试使用 `httpx.AsyncClient` 通过 ASGI transport 直接调用应用，无需启动真实服务器，但会连接真实数据库。

**当前测试结果：15 passed ✅**

---

## 开发说明

### 添加新接口

1. 在 `app/models/models.py` 添加或修改 ORM 模型
2. 在 `app/schemas/` 创建对应的 Pydantic schema
3. 在 `app/services/` 实现业务逻辑（继承 `BaseService`）
4. 在 `app/api/v1/` 创建 Router，注册到 `router.py`

### 数据库迁移（Alembic）

```bash
# 初始化（首次）
alembic init alembic

# 生成迁移文件
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head
```

---

## 容器化部署（Docker）

### 文件结构

```
DVDRentalSystem/
├── Dockerfile                  # 后端镜像（多阶段构建）
├── .dockerignore
├── docker-compose.yml          # 完整编排（含内置 PostgreSQL）
├── docker-compose.host-db.yml  # 覆盖文件：使用宿主机已有 PostgreSQL
└── .env.example                # 环境变量模板
```

### 方案一：完整容器化（推荐新部署）

启动 PostgreSQL + 后端 + 前端三个服务：

```bash
cd DVDRentalSystem

# 复制并按需修改环境变量
cp .env.example .env

# 构建并启动（首次需导入数据，见下方说明）
docker compose up -d --build

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f backend
```

访问 **http://localhost** 打开前端管理界面，**http://localhost:8000/docs** 查看后端 API 文档。

**数据库初始化数据**

`docker/initdb/01_dvdrental.sql` 是从真实数据库导出的完整 dump（结构 + 数据），PostgreSQL 容器在 **首次启动**（数据卷为空时）会自动执行该脚本，无需手动导入。

如需更新 dump（数据有变化时）：

```bash
pg_dump -h localhost -p 5432 -U postgres \
  --no-owner --no-acl --format=plain \
  --file=docker/initdb/01_dvdrental.sql \
  dvdrental

# 重建容器以应用新数据（会清空旧数据卷）
docker compose down -v && docker compose up -d --build
```

### 方案二：连接宿主机 PostgreSQL

保留现有宿主机数据库，只容器化后端和前端：

```bash
# macOS / Windows（Docker Desktop）
docker compose -f docker-compose.yml -f docker-compose.host-db.yml up -d --build

# Linux（宿主机 IP 通常为 172.17.0.1）
POSTGRES_HOST=172.17.0.1 \
docker compose -f docker-compose.yml -f docker-compose.host-db.yml up -d --build
```

### 单独构建镜像

```bash
# 仅构建后端
docker build -t dvdrental-backend:latest .

# 运行后端（连接宿主机 PostgreSQL，macOS/Windows）
docker run -d \
  -p 8000:8000 \
  -e POSTGRES_HOST=host.docker.internal \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=dvdrental \
  dvdrental-backend:latest
```

### 端口说明

| 服务 | 容器端口 | 宿主机默认端口 | 环境变量 |
|------|---------|--------------|---------|
| frontend (Nginx) | 80 | 80 | `FRONTEND_PORT` |
| backend (Uvicorn) | 8000 | 8000 | `BACKEND_PORT` |
| db (PostgreSQL) | 5432 | 5433 | `DB_HOST_PORT` |

> 内置 PostgreSQL 默认映射到宿主机 **5433**，避免与本地已有的 5432 端口冲突。
