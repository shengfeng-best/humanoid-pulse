from email import message_from_string
from email.header import decode_header
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.send_email import issue_subject, send_issue_email

FIXTURE = Path(__file__).parent / "fixtures" / "sample-issue.md"
SUBJECT = "人形脉冲 №01 · 2026.07.14–07.20"


def _decode_header(value: str) -> str:
    parts: list[str] = []
    for chunk, charset in decode_header(value):
        if isinstance(chunk, bytes):
            parts.append(chunk.decode(charset or "utf-8"))
        else:
            parts.append(chunk)
    return "".join(parts)


@pytest.fixture
def smtp_env(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.163.com")
    monkeypatch.setenv("SMTP_PORT", "465")
    monkeypatch.setenv("SMTP_USER", "user@163.com")
    monkeypatch.setenv("SMTP_PASS", "secret")
    monkeypatch.setenv("SMTP_FROM", "人形脉冲 <user@163.com>")


@pytest.fixture
def email_html(tmp_path):
    path = tmp_path / "email.html"
    path.write_text(
        "<html><body><p>在线阅读：https://example.com/issues/01/</p></body></html>",
        encoding="utf-8",
    )
    return path


def _mock_smtp_context():
    mock_smtp = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_smtp)
    mock_ctx.__exit__ = MagicMock(return_value=False)
    return mock_smtp, mock_ctx


def test_send_uses_smtp_ssl_on_465(smtp_env, email_html):
    mock_smtp, mock_ctx = _mock_smtp_context()
    with patch("scripts.send_email.smtplib.SMTP_SSL", return_value=mock_ctx) as ssl_cls:
        send_issue_email(email_html, SUBJECT)

    ssl_cls.assert_called_once_with("smtp.163.com", 465)
    mock_smtp.login.assert_called_once_with("user@163.com", "secret")
    mock_smtp.sendmail.assert_called_once()
    _, recipients, raw = mock_smtp.sendmail.call_args[0]
    assert recipients == ["15639028969@163.com", "shengfeng@openloong.net"]
    parsed = message_from_string(raw)
    assert _decode_header(parsed["Subject"]) == SUBJECT


def test_send_uses_starttls_on_other_port(smtp_env, email_html, monkeypatch):
    monkeypatch.setenv("SMTP_PORT", "587")
    mock_smtp, mock_ctx = _mock_smtp_context()
    with patch("scripts.send_email.smtplib.SMTP", return_value=mock_ctx) as smtp_cls:
        send_issue_email(email_html, "test subject")

    smtp_cls.assert_called_once_with("smtp.163.com", 587)
    mock_smtp.starttls.assert_called_once()
    mock_smtp.sendmail.assert_called_once()


def test_missing_smtp_pass_raises(smtp_env, email_html, monkeypatch):
    monkeypatch.delenv("SMTP_PASS")
    with pytest.raises(ValueError, match="SMTP_PASS"):
        send_issue_email(email_html, "subject")


def test_pulse_to_override(smtp_env, email_html, monkeypatch):
    monkeypatch.setenv("PULSE_TO", "a@example.com,b@example.com")
    mock_smtp, mock_ctx = _mock_smtp_context()
    with patch("scripts.send_email.smtplib.SMTP_SSL", return_value=mock_ctx):
        send_issue_email(email_html, "subject")

    assert mock_smtp.sendmail.call_args[0][1] == ["a@example.com", "b@example.com"]


def test_issue_subject_format(tmp_path):
    import shutil

    issue_dir = tmp_path / "2026-07-01"
    issue_dir.mkdir()
    shutil.copy(FIXTURE, issue_dir / "issue.md")
    assert issue_subject(issue_dir) == SUBJECT
