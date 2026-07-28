"""OpenCLI transport for read-only Zhihu collection."""
from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from .xiaohongshu_client import _NAVIGATION_REJECTED, _decode_json, _unwrap


class OpenCLIZhihuError(RuntimeError):
    pass


@dataclass(frozen=True)
class OpenCLIZhihuConfig:
    command: str = "opencli"
    timeout_seconds: float = 120.0


class OpenCLIZhihuClient:
    def __init__(self, config: OpenCLIZhihuConfig | None = None) -> None:
        self.config = config or OpenCLIZhihuConfig()
        self._base = shlex.split(os.environ.get("OPENCLI_COMMAND") or self.config.command)
        if not self._base:
            raise OpenCLIZhihuError("OPENCLI_COMMAND is empty")

    def user_articles(self, user: str, limit: int = 20) -> list[dict]:
        try:
            return self._rows("zhihu", "user-articles", user, "--limit", str(limit), "-f", "json")
        except OpenCLIZhihuError:
            return self._user_articles_first_page(user, limit)

    def user_answers(self, user: str, limit: int = 20) -> list[dict]:
        return self._rows("zhihu", "user-answers", user, "--limit", str(limit), "-f", "json")

    def answer_detail(self, target: str) -> dict:
        payload = _unwrap(self._run("zhihu", "answer-detail", target, "-f", "json"))
        if isinstance(payload, list) and payload:
            return payload[0] if isinstance(payload[0], dict) else {}
        return payload if isinstance(payload, dict) else {}

    def article_detail(self, url: str) -> dict:
        with tempfile.TemporaryDirectory(prefix="omnisource-zhihu-") as output:
            payload = _unwrap(self._run(
                "zhihu", "download", "--url", url, "--output", output,
                "--download-images", "false", "-f", "json",
            ))
            meta = payload[0] if isinstance(payload, list) and payload and isinstance(payload[0], dict) else {}
            saved = Path(str(meta.get("saved") or ""))
            content = saved.read_text(encoding="utf-8") if saved.is_file() else ""
            return {**meta, "content": content}

    def _user_articles_first_page(self, user: str, limit: int) -> list[dict]:
        """Read only the first API page when OpenCLI rejects Zhihu's HTTP next URL."""
        slug = user.rstrip("/").split("/")[-1]
        session = f"omnisource-zhihu-{uuid.uuid4().hex[:10]}"
        endpoint = (
            f"https://www.zhihu.com/api/v4/members/{slug}/articles"
            "?limit=20&offset=0&include=data%5B*%5D.voteup_count%2Ccomment_count"
        )
        script = (
            "(async()=>{const r=await fetch(" + json.dumps(endpoint)
            + ",{credentials:'include'});return {status:r.status,body:await r.json()}})()"
        )
        self._run("browser", session, "open", "https://www.zhihu.com", "--window", "background")
        try:
            payload = self._run("browser", session, "eval", script)
        finally:
            try:
                self._run("browser", session, "close")
            except OpenCLIZhihuError:
                pass
        if not isinstance(payload, dict) or payload.get("status") != 200:
            raise OpenCLIZhihuError("Zhihu user articles first-page request failed")
        body = payload.get("body") or {}
        data = body.get("data") if isinstance(body, dict) else None
        if not isinstance(data, list):
            raise OpenCLIZhihuError("Zhihu user articles first page returned malformed data")
        rows = []
        for index, article in enumerate(data[:limit]):
            if not isinstance(article, dict) or not article.get("id"):
                continue
            rows.append({
                "rank": index + 1,
                "title": str(article.get("title") or ""),
                "author": str((article.get("author") or {}).get("name") or ""),
                "votes": article.get("voteup_count") or 0,
                "comments": article.get("comment_count") or 0,
                "created": article.get("created") or article.get("updated") or 0,
                "excerpt": str(article.get("excerpt") or ""),
                "url": f"https://zhuanlan.zhihu.com/p/{article['id']}",
            })
        return rows

    def _rows(self, *args: str) -> list[dict]:
        payload = _unwrap(self._run(*args))
        if not isinstance(payload, list):
            raise OpenCLIZhihuError("OpenCLI Zhihu command returned an unexpected JSON shape")
        return [row for row in payload if isinstance(row, dict)]

    def _run(self, *args: str):
        executable = self._base[0]
        if not (os.path.isabs(executable) or shutil.which(executable)):
            raise OpenCLIZhihuError("OpenCLI is not installed or not on PATH")
        for attempt in range(2):
            try:
                proc = subprocess.run(
                    [*self._base, *args], capture_output=True, text=True,
                    timeout=self.config.timeout_seconds, check=False,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise OpenCLIZhihuError(f"Could not run OpenCLI Zhihu command: {exc}") from exc
            if proc.returncode:
                detail = (proc.stderr or proc.stdout or "").strip()[:500]
                if attempt == 0 and _NAVIGATION_REJECTED in detail.lower():
                    time.sleep(1)
                    continue
                raise OpenCLIZhihuError(f"OpenCLI exited with status {proc.returncode}: {detail}")
            try:
                return _decode_json(proc.stdout)
            except (ValueError, json.JSONDecodeError) as exc:
                raise OpenCLIZhihuError("OpenCLI Zhihu command did not return JSON") from exc
        raise AssertionError("OpenCLI retry loop did not return or raise")
