import logging
import socket
import smtplib
from email.mime.text import MIMEText


# Set up logging configuration (file, format, and log level)
def setup_logging(log_file: str):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


# Evaluate if a value is OK, exceeds the soft limit, or exceeds the hard limit
def eval_threshold(soft: float, hard: float, value: float):
    """Returns 'ok', 'soft', or 'hard' depending on the given value."""
    if value > hard:
        return "hard"
    if value > soft:
        return "soft"
    return "ok"


# Send an email alert using SMTP configuration
def _send_email(cfg: dict, subject: str, body: str):
    # Skip sending if SMTP is disabled in the config
    if not cfg.get("enabled", "false").lower() == "true":
        logging.info("SMTP disabled; skipping email.")
        return
    try:
        # Read SMTP configuration values
        server = cfg.get("server")
        port = int(cfg.get("port", 25))
        use_tls = cfg.get("use_tls", "false").lower() == "true"
        username = cfg.get("username")
        password = cfg.get("password")
        sender = cfg.get("from")
        recipient = cfg.get("to")

        # Create email message
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient

        # Connect to the mail server and send message
        with smtplib.SMTP(server, port, timeout=10) as s:
            if use_tls:
                s.starttls()
            if username and password:
                s.login(username, password)
            s.send_message(msg)

        logging.info("Alarm email sent to %s", recipient)
    except Exception as e:
        logging.error("Email sending failed: %s", e)


# Check a metric against its limits, log the result, and send email if hard limit is exceeded
def check_and_alert(name: str, value: float, soft: float, hard: float, smtp_cfg: dict, unit: str = "%"):
    """
    Compares a given metric to its thresholds.
    Logs the result, and sends an email if the 'hard' limit is reached.
    """
    host = socket.gethostname()
    state = eval_threshold(soft, hard, value)

    if state == "hard":
        msg = f"{host}: {name.upper()} hard limit exceeded ({value}{unit}) [Soft {soft}{unit} | Hard {hard}{unit}]"
        logging.warning(msg)
        _send_email(smtp_cfg, f"[ALERT] {name.upper()} hard limit!", msg)
    elif state == "soft":
        msg = f"{host}: {name.upper()} soft limit exceeded ({value}{unit}) [Soft {soft}{unit} | Hard {hard}{unit}]"
        logging.info(msg)
    else:
        logging.info("%s: %s OK (%s%s)", host, name.upper(), value, unit)

    return state  # Useful for testing or automation
