from __future__ import annotations

import argparse
import csv
import json
import mimetypes
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from chat import ARTIFACTS_DIR, now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).parent
APP_DIR = ROOT / "app"
TRANSCRIPTS_DIR = ROOT / "transcripts"
RUNS_DIR = ROOT / "runs"

HISTORY_WINDOW = 5
MAX_TOOL_ROUNDS = 4

METRIC_KEYS = (
    "case_accuracy",
    "tool_routing_accuracy",
    "argument_accuracy",
    "multiturn_accuracy",
)

_provider_cache: dict[str, object] = {}
_transcript_cache: dict[str, dict] = {}


def get_provider(name: str):
    if name not in _provider_cache:
        _provider_cache[name] = make_provider(name)
    return _provider_cache[name]


def get_transcript(session_id: str, provider_name: str, version: str) -> dict:
    if session_id not in _transcript_cache:
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), "ui", timestamp])
        _transcript_cache[session_id] = {
            "transcript_id": transcript_id,
            "path": TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json",
            "created_at": now_iso(),
            "turns": [],
        }
    return _transcript_cache[session_id]


def load_version_log() -> list[dict]:
    """Đọc version_log.csv (do #2 sở hữu) — chỉ đọc, không sửa."""
    path = ARTIFACTS_DIR / "version_log.csv"
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def collect_evidence() -> dict:
    """Gom evidence từ runs/*.json + version_log.csv để UI so sánh các version.

    Mỗi version chỉ giữ run mới nhất (theo generated_at) để bảng so sánh không
    bị trùng dòng khi một version được chạy lại nhiều lần.
    """
    runs: dict[str, dict] = {}
    for path in sorted(RUNS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        version = str(data.get("version") or path.stem.split("_")[0])
        summary = data.get("summary") or {}
        cases = []
        for item in data.get("results") or []:
            result = item.get("result") or {}
            cases.append({
                "id": item.get("id"),
                "is_multiturn": bool(item.get("is_multiturn")),
                "skill": (item.get("metadata") or {}).get("skill"),
                "what_it_tests": (item.get("metadata") or {}).get("what_it_tests"),
                "input": item.get("input"),
                "expect": item.get("expect"),
                "passed": bool(result.get("passed")),
                "routing_correct": result.get("routing_correct"),
                "args_correct": result.get("args_correct"),
                "failure_type": result.get("failure_type"),
                "observed_mismatch": result.get("observed_mismatch"),
                "failures": result.get("failures") or [],
                "actual_tool_calls": result.get("actual_tool_calls") or [],
                "actual_text": result.get("actual_text"),
            })

        entry = {
            "version": version,
            "run_file": f"runs/{path.name}",
            "artifact_version": data.get("artifact_version"),
            "provider": data.get("provider"),
            "model": data.get("model"),
            "suite": data.get("suite"),
            "generated_at": data.get("generated_at") or "",
            "metrics": {key: summary.get(key) for key in METRIC_KEYS},
            "total_cases": summary.get("total_cases"),
            "measured_cases": summary.get("measured_cases"),
            "passed_cases": summary.get("passed_cases"),
            "provider_error_cases": summary.get("provider_error_cases"),
            "failure_counts": summary.get("failure_counts") or {},
            "observed_mismatch_counts": summary.get("observed_mismatch_counts") or {},
            # Metric chỉ hợp lệ khi không có provider error và đo đủ số case.
            "metrics_valid": (
                summary.get("provider_error_cases") == 0
                and summary.get("measured_cases") == summary.get("total_cases")
            ),
            "cases": cases,
        }

        prev = runs.get(version)
        if prev is None or entry["generated_at"] >= prev["generated_at"]:
            runs[version] = entry

    versions = sorted(runs.values(), key=lambda item: item["version"])

    # Danh sách case theo thứ tự của version đầu tiên, cộng thêm case chỉ có ở version sau.
    case_ids: list[str] = []
    for entry in versions:
        for case in entry["cases"]:
            if case["id"] not in case_ids:
                case_ids.append(case["id"])

    return {
        "versions": versions,
        "case_ids": case_ids,
        "version_log": load_version_log(),
    }


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self._send_json(404, {"error": "not_found"})
            return
        content_type, _ = mimetypes.guess_type(str(path))
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        route = urlparse(self.path).path
        if route in ("", "/"):
            self._send_file(APP_DIR / "index.html")
            return
        if route == "/api/evidence":
            try:
                self._send_json(200, collect_evidence())
            except Exception as exc:
                self._send_json(500, {"error": f"{type(exc).__name__}: {exc}"})
            return
        candidate = (APP_DIR / route.lstrip("/")).resolve()
        app_root = APP_DIR.resolve()
        if candidate == app_root or app_root in candidate.parents:
            self._send_file(candidate)
            return
        self._send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/chat":
            self._send_json(404, {"error": "not_found"})
            return

        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid_json"})
            return

        message = (payload.get("message") or "").strip()
        version = payload.get("version") or "v0"
        provider_name = payload.get("provider") or "openrouter"
        session_id = payload.get("session_id") or "default"
        history = payload.get("history") or []

        if not message:
            self._send_json(400, {"error": "empty_message"})
            return

        try:
            system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
            tools_path = ARTIFACTS_DIR / "tools.yaml"
            system_prompt = system_prompt_path.read_text(encoding="utf-8")
            openai_tools = to_openai_tools(load_tool_declarations(tools_path))
            provider = get_provider(provider_name)
            artifact_version = build_artifact_version(version, system_prompt_path, tools_path)

            messages = [
                {"role": "system", "content": system_prompt},
                *trim_history(history, HISTORY_WINDOW),
                {"role": "user", "content": message},
            ]

            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=openai_tools,
                model=None,
                max_tool_rounds=MAX_TOOL_ROUNDS,
            )

            transcript = get_transcript(session_id, provider_name, version)
            transcript["turns"].append({
                "turn_index": len(transcript["turns"]) + 1,
                "started_at": now_iso(),
                "user": message,
                **result,
                **artifact_version_dict(artifact_version),
                "ended_at": now_iso(),
            })
            write_transcript(transcript["path"], {
                "transcript_id": transcript["transcript_id"],
                "provider": provider_name,
                "system_prompt": str(system_prompt_path),
                "tools": str(tools_path),
                "history_window": HISTORY_WINDOW,
                "max_tool_rounds": MAX_TOOL_ROUNDS,
                "created_at": transcript["created_at"],
                "turns": transcript["turns"],
            })

            self._send_json(200, {
                **result,
                "artifact_version": artifact_version.artifact_version,
                "transcript_path": str(transcript["path"]),
            })
        except Exception as exc:
            self._send_json(500, {"error": f"{type(exc).__name__}: {exc}"})

    def log_message(self, fmt: str, *args) -> None:
        print("%s - %s" % (self.address_string(), fmt % args))


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal stdlib HTTP server for the Research Agent HTML UI.")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    print(f"Research Agent UI: http://localhost:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
