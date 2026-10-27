import json, os, subprocess, sys, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

QSUM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "qsum")
REPLY = "- ERROR disk full on volume 3\n- done in 4.2 s"


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, obj):
        b = json.dumps(obj).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        self._send({"data": [{"id": "fake-model"}]})

    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        self._send({"choices": [{"message": {"content": REPLY}}]})


def serve():
    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def run(args, text, env_extra):
    env = {**os.environ, **env_extra}
    return subprocess.run([sys.executable, QSUM] + args, input=text, capture_output=True, text=True, env=env, timeout=60)


def test_help_exits_zero():
    r = run(["--help"], "", {})
    assert r.returncode == 0 and "usage: qsum" in r.stdout


def test_digest_and_verify_ok(tmp_path):
    srv = serve()
    try:
        env = {"QSUM_ENDPOINT": "http://127.0.0.1:%d" % srv.server_port, "QSUM_VERIFY_LOG": str(tmp_path / "v.log")}
        r = run(["--verify"], "start\nERROR disk full on volume 3\ndone in 4.2 s\n", env)
    finally:
        srv.shutdown()
    assert r.returncode == 0
    assert "ERROR disk full on volume 3" in r.stdout
    assert "verify OK" in r.stderr


def test_verify_flags_invented_line(tmp_path):
    srv = serve()
    try:
        env = {"QSUM_ENDPOINT": "http://127.0.0.1:%d" % srv.server_port, "QSUM_VERIFY_LOG": str(tmp_path / "v.log")}
        r = run(["--verify"], "nothing relevant here\n", env)
    finally:
        srv.shutdown()
    assert "WARNING 2/2" in r.stderr
    assert "MISSING" in (tmp_path / "v.log").read_text()
