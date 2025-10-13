import logging
import socket
import smtplib
from email.mime.text import MIMEText

def setup_logging(log_file: str):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

def eval_threshold(soft: float, hard: float, value: float):
    """Rein funktional (gut testbar): liefert 'ok' | 'soft' | 'hard'."""
    if value > hard:
        return "hard"
    if value > soft:
        return "soft"
    return "ok"

def _send_email(cfg: dict, subject: str, body: str):
    if not cfg.get("enabled", "false").lower() == "true":
        logging.info("SMTP disabled; skipping email.")
        return
    try:
        server = cfg.get("server")
        port = int(cfg.get("port", 25))
        use_tls = cfg.get("use_tls", "false").lower() == "true"
        username = cfg.get("username")
        password = cfg.get("password")
        sender = cfg.get("from")
        recipient = cfg.get("to")

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient

        with smtplib.SMTP(server, port, timeout=10) as s:
            if use_tls:
                s.starttls()
            if username and password:
                s.login(username, password)
            s.send_message(msg)
        logging.info("Alarm-E-Mail gesendet an %s", recipient)
    except Exception as e:
        logging.error("E-Mail-Versand fehlgeschlagen: %s", e)

def check_and_alert(name: str, value: float, soft: float, hard: float, smtp_cfg: dict, unit: str = "%"):
    """
    Prüft Wert gegen Soft/Hard, loggt und sendet bei 'hard' zusätzlich eine Mail.
    """
    host = socket.gethostname()
    state = eval_threshold(soft, hard, value)

    if state == "hard":
        msg = f"{host}: {name.upper()} Hardlimit überschritten ({value}{unit}) [Soft {soft}{unit} | Hard {hard}{unit}]"
        logging.warning(msg)
        _send_email(smtp_cfg, f"[ALARM] {name.upper()} Hardlimit!", msg)
    elif state == "soft":
        msg = f"{host}: {name.upper()} Softlimit überschritten ({value}{unit}) [Soft {soft}{unit} | Hard {hard}{unit}]"
        logging.info(msg)
    else:
        logging.info("%s: %s OK (%s%s)", host, name.upper(), value, unit)

    return state  # praktisch für (Auto-)Tests