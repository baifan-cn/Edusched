#!/usr/bin/env python3
"""
简单的应用启动脚本
"""

import os
import sys
import uvicorn

# 设置环境变量
os.environ.update({
    'DB_HOST': 'localhost',
    'DB_PORT': '5432',
    'DB_NAME': 'edusched',
    'DB_USER': 'edusched',
    'DB_PASSWORD': 'edusched123',
    'REDIS_HOST': 'localhost',
    'REDIS_PORT': '6379',
    'REDIS_PASSWORD': 'edusched123',
    'SECURITY_SECRET_KEY': 'your-super-secret-key-here-make-it-long-enough',
    'OIDC_ISSUER': 'http://localhost:8080/auth/realms/edusched',
    'OIDC_CLIENT_ID': 'edusched-client',
    'OIDC_CLIENT_SECRET': 'edusched-secret'
})

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    print("正在启动Edusched应用...")
    print("环境变量已设置")
    print("数据库连接信息:")
    print(f"  PostgreSQL: {os.environ['DB_HOST']}:{os.environ['DB_PORT']}")
    print(f"  Redis: {os.environ['REDIS_HOST']}:{os.environ['REDIS_PORT']}")
    
    try:
        uvicorn.run(
            "edusched.api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()