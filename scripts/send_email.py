from __future__ import annotations

import argparse
import mimetypes
import os
import re
import smtplib
from email.message import EmailMessage
from email.utils import parseaddr
from pathlib import Path

from scripts.build import format_date_range
from scripts.parse_issue import parse_issue

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECIPIENTS = ["15639028969@163.com", "shengfeng@openloong.net"]
REQUIRED_ENV = ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS", "SMTP_FROM")

# Match src="assets/..." or Pages absolute .../assets/...
_IMG_SRC_RE = re.compile(
    r'(<img\b[^>]*?\bsrc=")([^"]+)(")',
    flags=re.I,
)


def load_dotenv(path: Path | None = None) -> None:
    """Load KEY=VALUE lines from .env without overriding existing env vars."""
    env_path = path or REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value


def _smtp_config() -> dict[str, str | int]:
    missing = [key for key in REQUIRED_ENV if not os.environ.get(key)]
    if missing:
        raise ValueError(f"missing required env: {', '.join(missing)}")
    return {
        "host": os.environ["SMTP_HOST"],
        "port": int(os.environ["SMTP_PORT"]),
        "user": os.environ["SMTP_USER"],
        "password": os.environ["SMTP_PASS"],
        "from_addr": os.environ["SMTP_FROM"],
    }


def _default_recipients() -> list[str]:
    raw = os.environ.get("PULSE_TO", "").strip()
    if raw:
        return [addr.strip() for addr in raw.split(",") if addr.strip()]
    return list(DEFAULT_RECIPIENTS)


def _html_to_plain(html: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
    text = re.sub(r"</p>", "\n\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _resolve_asset(issue_dir: Path, src: str) -> Path | None:
    """Map img src to a local file under issue_dir."""
    src = src.strip()
    if src.startswith("cid:"):
        return None
    # Absolute Pages URL → assets/...
    marker = "/assets/"
    if marker in src.replace("\\", "/"):
        rel = "assets/" + src.replace("\\", "/").split(marker, 1)[1]
        candidate = issue_dir / rel
        return candidate if candidate.is_file() else None
    # Relative assets/...
    if src.startswith("assets/"):
        candidate = issue_dir / src
        return candidate if candidate.is_file() else None
    return None


def inline_images_as_cid(html: str, issue_dir: Path) -> tuple[str, list[tuple[str, Path]]]:
    """Rewrite local/Pages image src to cid: and collect files to attach."""
    attachments: list[tuple[str, Path]] = []
    seen: dict[str, str] = {}  # path str → cid

    def repl(match: re.Match[str]) -> str:
        prefix, src, suffix = match.group(1), match.group(2), match.group(3)
        path = _resolve_asset(issue_dir, src)
        if path is None:
            return match.group(0)
        key = str(path.resolve())
        if key not in seen:
            cid = f"pulse-img-{len(seen) + 1}"
            seen[key] = cid
            attachments.append((cid, path))
        return f"{prefix}cid:{seen[key]}{suffix}"

    return _IMG_SRC_RE.sub(repl, html), attachments


def send_issue_email(
    email_html_path: Path,
    subject: str,
    to: list[str] | None = None,
    issue_dir: Path | None = None,
) -> None:
    load_dotenv()
    cfg = _smtp_config()
    recipients = to if to is not None else _default_recipients()

    email_html_path = Path(email_html_path)
    issue_dir = Path(issue_dir) if issue_dir is not None else email_html_path.parent

    html = email_html_path.read_text(encoding="utf-8")
    html, attachments = inline_images_as_cid(html, issue_dir)
    plain = _html_to_plain(html)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = str(cfg["from_addr"])
    msg["To"] = ", ".join(recipients)
    msg.set_content(plain)
    msg.add_alternative(html, subtype="html")

    if attachments:
        html_part = msg.get_payload()[-1]
        for cid, path in attachments:
            mime, _ = mimetypes.guess_type(str(path))
            if not mime or not mime.startswith("image/"):
                mime = "image/jpeg"
            maintype, subtype = mime.split("/", 1)
            html_part.add_related(
                path.read_bytes(),
                maintype=maintype,
                subtype=subtype,
                cid=cid,
            )

    _, envelope_from = parseaddr(str(cfg["from_addr"]))
    sender = envelope_from or str(cfg["user"])

    if cfg["port"] == 465:
        with smtplib.SMTP_SSL(str(cfg["host"]), int(cfg["port"])) as smtp:
            smtp.login(str(cfg["user"]), str(cfg["password"]))
            smtp.sendmail(sender, recipients, msg.as_string())
    else:
        with smtplib.SMTP(str(cfg["host"]), int(cfg["port"])) as smtp:
            smtp.starttls()
            smtp.login(str(cfg["user"]), str(cfg["password"]))
            smtp.sendmail(sender, recipients, msg.as_string())


def issue_subject(issue_dir: Path) -> str:
    data = parse_issue(Path(issue_dir) / "issue.md")
    number_padded = f"{int(data['number']):02d}"
    date_range = format_date_range(data["date_start"], data["date_end"])
    return f"人形脉冲 №{number_padded} · {date_range}"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Send Pulse issue email via SMTP")
    parser.add_argument("issue_dir", type=Path, help="Path to issue directory")
    args = parser.parse_args(argv)

    issue_dir = Path(args.issue_dir)
    email_path = issue_dir / "email.html"
    if not email_path.is_file():
        raise SystemExit(f"email.html not found: {email_path}")

    subject = issue_subject(issue_dir)
    try:
        send_issue_email(email_path, subject, issue_dir=issue_dir)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    print(f"Sent: {subject}")


if __name__ == "__main__":
    main()
