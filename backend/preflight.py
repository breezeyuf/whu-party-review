"""Read-only startup checks. No schema changes or credentials in output."""
from pathlib import Path
import sys


def main():
    try:
        from sqlalchemy import text
        from database import engine
        from config import STORAGE_DIR
        from ai.parser import parse_version_file  # noqa: F401
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        dist = Path(__file__).resolve().parents[1] / "frontend" / "dist" / "index.html"
        if not dist.is_file():
            print("前端尚未构建：请在 frontend 中运行 npm ci 和 npm run build。")
            return 1
        print(f"启动检查通过。材料目录：{STORAGE_DIR}")
        print("服务地址由 HOST/PORT 配置，默认 http://127.0.0.1:8000")
        return 0
    except ImportError:
        print("缺少后端依赖。请按 RUN.md 创建虚拟环境并安装 requirements.txt。")
    except Exception:
        print("数据库连接失败。请检查 PostgreSQL 是否启动，以及 backend/.env 的 DATABASE_URL。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
