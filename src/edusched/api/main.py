"""FastAPI应用主文件。

包含应用配置、中间件、路由注册和启动逻辑。
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from edusched.core.config import get_settings
from edusched.infrastructure.database.connection import init_db, close_db
from edusched.api.routers import (
    health,
    schools,
    teachers,
    courses,
    timetables,
    scheduling,
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 获取配置
settings = get_settings()

# 配置Sentry
if settings.observability.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.observability.sentry_dsn,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
        environment=settings.environment,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理。"""
    # 启动时
    logger.info("正在启动Edusched应用...")
    
    # 初始化数据库
    try:
        await init_db()
        logger.info("数据库连接初始化成功")
    except Exception as e:
        logger.error(f"数据库连接初始化失败: {e}")
        raise
    
    # 初始化其他服务
    # TODO: 初始化Redis、调度引擎等
    
    logger.info("Edusched应用启动完成")
    
    yield
    
    # 关闭时
    logger.info("正在关闭Edusched应用...")
    
    # 关闭数据库连接
    try:
        await close_db()
        logger.info("数据库连接已关闭")
    except Exception as e:
        logger.error(f"关闭数据库连接时出错: {e}")
    
    logger.info("Edusched应用已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    description="智能教育调度平台 - 为学校生成可行且优化的课程表",
    version=settings.app_version,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)


# 添加中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """添加处理时间头。"""
    import time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def add_tenant_header(request: Request, call_next):
    """添加租户头。"""
    # 从请求头或路径中提取租户ID
    tenant_id = request.headers.get("X-Tenant-ID", settings.default_tenant)
    request.state.tenant_id = tenant_id
    response = await call_next(request)
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录请求日志。"""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} - {response.status_code}")
    return response


# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 添加可信主机中间件
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # 在生产环境中应该限制具体的主机名
    )


# 异常处理器
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理器。"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP错误",
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path,
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器。"""
    return JSONResponse(
        status_code=422,
        content={
            "error": "请求验证错误",
            "message": "请求数据格式不正确",
            "details": exc.errors(),
            "path": request.url.path,
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器。"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "内部服务器错误",
            "message": "服务器内部错误，请稍后重试",
            "path": request.url.path,
        }
    )


# 健康检查端点
@app.get("/")
async def root():
    """根端点。"""
    return {
        "message": "欢迎使用Edusched智能教育调度平台",
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/health")
async def health_check():
    """健康检查端点。"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}


# 注册路由
app.include_router(health.router, prefix="/api/v1", tags=["健康检查"])
app.include_router(schools.router, prefix="/api/v1/schools", tags=["学校管理"])
app.include_router(teachers.router, prefix="/api/v1/teachers", tags=["教师管理"])
app.include_router(courses.router, prefix="/api/v1/courses", tags=["课程管理"])
app.include_router(timetables.router, prefix="/api/v1/timetables", tags=["时间表管理"])
app.include_router(scheduling.router, prefix="/api/v1/scheduling", tags=["调度引擎"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "edusched.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers,
        log_level=settings.observability.log_level.lower(),
    )