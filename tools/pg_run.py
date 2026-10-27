"""启动一个供本机联调/回归使用的临时 PostgreSQL（pgserver 自带 16.x 二进制）。

用法：
    python tools/pg_run.py [pgdata_dir]

默认数据目录 `_tmp/pgdata`；连接串同时写入数据目录旁的 `pg_uri.txt`，方便其它终端读取。
进程常驻，Ctrl+C 或进程结束时停库。需要 Python ≤3.12 的 pgserver 环境，见 docs/RUN.md。
"""
import sys
import time
from pathlib import Path

import pgserver

pgdata = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "_tmp/pgdata").resolve()
pgdata.mkdir(parents=True, exist_ok=True)
srv = pgserver.get_server(pgdata, cleanup_mode="stop")
uri = srv.get_uri()
uri_file = pgdata.parent / "pg_uri.txt"
uri_file.write_text(uri, encoding="utf-8")
print(f"[pg] ready: {uri}", flush=True)
print(f"[pg] 连接串已写入 {uri_file}", flush=True)
try:
    while True:
        time.sleep(3600)
except KeyboardInterrupt:
    pass
finally:
    srv.cleanup()
    print("[pg] stopped", flush=True)
