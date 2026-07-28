"""OpenCLI transport for Xiaohongshu.

This module deliberately knows nothing about OmniSource ``Signal`` objects. It
only invokes OpenCLI and normalizes its JSON output, keeping browser-session
details and signed ``xsec_token`` URLs inside the transport boundary.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import time
from dataclasses import dataclass


_ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
_XSEC_RE = re.compile(r"([?&]xsec_token=)[^&#\s]+", re.I)
_NAVIGATION_REJECTED = "navigation rejected"


class OpenCLIError(RuntimeError):
    """An OpenCLI command could not be executed or returned unusable data."""


@dataclass(frozen=True)
class OpenCLIConfig:
    command: str = "opencli"
    timeout_seconds: float = 120.0


class OpenCLIXiaohongshuClient:
    def __init__(self, config: OpenCLIConfig | None = None) -> None:
        self.config = config or OpenCLIConfig()
        configured = os.environ.get("OPENCLI_COMMAND") or self.config.command
        self._base_command = shlex.split(configured)
        if not self._base_command:
            raise OpenCLIError("OPENCLI_COMMAND is empty")

    def user_notes(self, user_id: str, limit: int = 20) -> list[dict]:
        payload = self._run("xiaohongshu", "user", user_id, "--limit", str(limit), "-f", "json")
        return _as_rows(payload)

    def note_detail(self, signed_url: str) -> dict:
        payload = self._run("xiaohongshu", "note", signed_url, "-f", "json")
        payload = _unwrap(payload)
        if isinstance(payload, list):
            # The note adapter commonly emits [{"field": "title", "value": ...}, ...].
            fields = {}
            for row in payload:
                if isinstance(row, dict) and row.get("field"):
                    fields[str(row["field"])] = row.get("value")
            return fields if fields else {"items": payload}
        if isinstance(payload, dict):
            return payload
        raise OpenCLIError("OpenCLI note returned an unexpected JSON shape")

    def _run(self, *args: str):
        executable = self._base_command[0]
        if not (os.path.isabs(executable) or shutil.which(executable)):
            raise OpenCLIError(
                "OpenCLI is not installed or not on PATH. Install OpenCLI and connect its Chrome Browser Bridge first."
            )
        for attempt in range(2):
            try:
                proc = subprocess.run(
                    [*self._base_command, *args],
                    capture_output=True,
                    text=True,
                    timeout=self.config.timeout_seconds,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise OpenCLIError(f"OpenCLI timed out after {self.config.timeout_seconds:g}s") from exc
            except OSError as exc:
                raise OpenCLIError(f"Could not start OpenCLI: {exc}") from exc

            if proc.returncode != 0:
                detail = _redact((proc.stderr or proc.stdout or "").strip())[:500]
                if attempt == 0 and _NAVIGATION_REJECTED in detail.lower():
                    time.sleep(1)
                    continue
                raise OpenCLIError(f"OpenCLI exited with status {proc.returncode}: {detail or 'no error output'}")
            try:
                return _decode_json(proc.stdout)
            except ValueError as exc:
                preview = _redact(proc.stdout.strip())[:300]
                raise OpenCLIError(f"OpenCLI did not return JSON: {preview or 'empty output'}") from exc
        raise AssertionError("OpenCLI retry loop did not return or raise")


def _decode_json(text: str):
    """Decode direct JSON or JSON surrounded by harmless CLI log lines."""
    cleaned = _ANSI_RE.sub("", text).strip()
    if not cleaned:
        raise ValueError("empty output")
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    decoded = []
    for index, char in enumerate(cleaned):
        if char not in "[{":
            continue
        try:
            value, end = decoder.raw_decode(cleaned[index:])
        except json.JSONDecodeError:
            continue
        decoded.append((index + end, value))
    if not decoded:
        raise ValueError("no JSON value")
    return max(decoded, key=lambda item: item[0])[1]


def _unwrap(payload):
    current = payload
    for _ in range(3):
        if not isinstance(current, dict):
            break
        for key in ("data", "results", "items", "notes", "feeds"):
            value = current.get(key)
            if isinstance(value, (list, dict)):
                current = value
                break
        else:
            break
    return current


def _as_rows(payload) -> list[dict]:
    rows = _unwrap(payload)
    if not isinstance(rows, list):
        raise OpenCLIError("OpenCLI user command returned an unexpected JSON shape")
    return [row for row in rows if isinstance(row, dict)]


def _redact(value: str) -> str:
    return _XSEC_RE.sub(r"\1<redacted>", value)
