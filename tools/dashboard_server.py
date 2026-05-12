"""
《江湖一生》製作人儀表板伺服器
讀取本地文件，提供 API 給 dashboard.html
用法：python tools/dashboard_server.py
瀏覽器開啟：http://localhost:7788
"""
import os, sys, json, re, glob, subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """多線程 HTTP 伺服器，支援並行請求"""
    daemon_threads = True

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
GDD_DIR = os.path.join(ROOT, "design", "gdd")
UX_DIR  = os.path.join(ROOT, "design", "ux")
PORT = 7788


def read_file_safe(path, tail=None, head=None):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
            if tail:  return "".join(lines[-tail:])
            if head:  return "".join(lines[:head])
            return "".join(lines)
    except Exception:
        return ""


SKIP_GDD = {"systems-index.md","design-canon.md","decision-log.md",
            "core-gdd.md","game-concept.md","ux-spec.md","entities.yaml"}

import time as _time
_cache = {}
def cached(key, ttl, fn):
    now = _time.time()
    if key not in _cache or now - _cache[key][0] > ttl:
        _cache[key] = (now, fn())
    return _cache[key][1]

def get_gdd_status():
    result = {"approved": [], "reviewed": [], "draft": [], "revision": []}
    for path in sorted(glob.glob(os.path.join(GDD_DIR, "*.md"))):
        fname = os.path.basename(path)
        if fname in SKIP_GDD:
            continue
        header = read_file_safe(path, head=5)
        name_match = re.search(r"^#[^#]\s*(.+?)(?:\s*GDD)?$", header, re.MULTILINE)
        name = name_match.group(1).strip() if name_match else fname.replace(".md","")
        name = re.sub(r"《江湖一生》[—\-\s]*", "", name).strip()
        if "已核准" in header:
            result["approved"].append({"file": fname, "name": name})
        elif "已審核" in header:
            result["reviewed"].append({"file": fname, "name": name})
        elif "修訂中" in header:
            result["revision"].append({"file": fname, "name": name})
        else:
            result["draft"].append({"file": fname, "name": name})
    result["total"] = sum(len(v) for v in result.values())
    result["done"] = len(result["approved"]) + len(result["reviewed"])
    return result


def get_ux_status():
    specs = []
    for path in sorted(glob.glob(os.path.join(UX_DIR, "*.md"))):
        fname = os.path.basename(path)
        if fname.startswith("_") or fname == "README.md":
            continue
        specs.append({"file": fname, "name": fname.replace(".md","").replace("-"," ")})
    return {"count": len(specs), "specs": specs}


def get_logs():
    qlog = read_file_safe(os.path.join(TOOLS, "qingxia_log.md"), tail=30)
    jlog = read_file_safe(os.path.join(TOOLS, "jingyi_log.md"), tail=30)
    return {"qingxia": qlog, "jingyi": jlog}


def get_queue_status():
    queue_path = os.path.join(TOOLS, "qingxia_tasks", "overnight_queue.md")
    content = read_file_safe(queue_path)
    pending = len(re.findall(r"Status: pending", content))
    done    = len(re.findall(r"Status: done", content))
    failed  = len(re.findall(r"Status: failed", content))
    jqueue  = read_file_safe(os.path.join(TOOLS, "jingyi_tasks", "queue.md"))
    j_pending = len(re.findall(r"Status: pending", jqueue))
    j_done    = len(re.findall(r"Status: done", jqueue))
    return {"qingxia": {"pending": pending, "done": done, "failed": failed},
            "jingyi":  {"pending": j_pending, "done": j_done}}


def get_agents():
    try:
        out = subprocess.check_output(["tasklist"], text=True, errors="replace")
        watchdog_ok = "6004" in out or "watchdog" in out.lower()
        py_count = out.lower().count("pythonw")
        return {"watchdog": py_count >= 4, "services": py_count}
    except Exception:
        return {"watchdog": False, "services": 0}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def send_json(self, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, content):
        body = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/" or path == "/dashboard":
            html_path = os.path.join(TOOLS, "dashboard.html")
            self.send_html(read_file_safe(html_path))
        elif path == "/api/gdd":
            self.send_json(get_gdd_status())
        elif path == "/api/ux":
            self.send_json(get_ux_status())
        elif path == "/api/logs":
            self.send_json(get_logs())
        elif path == "/api/queue":
            self.send_json(get_queue_status())
        elif path == "/api/agents":
            self.send_json(get_agents())
        elif path == "/api/all":
            self.send_json({
                "gdd":   cached("gdd",   30, get_gdd_status),
                "ux":    cached("ux",    60, get_ux_status),
                "logs":  get_logs(),          # 日誌不快取，每次即時
                "queue": cached("queue", 10, get_queue_status),
                "agents":cached("agents", 5, get_agents),
            })
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    print(f"儀表板啟動：http://localhost:{PORT}")
    ThreadingHTTPServer(("", PORT), Handler).serve_forever()
