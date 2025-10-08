import psutil
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# ---------------------------
# Konfiguration
# ---------------------------

CPU_THRESHOLD = 80        # Prozent
MEMORY_THRESHOLD = 80     # Prozent
DISK_THRESHOLD = 90       # Prozent
CHECK_INTERVAL = 60       # Sekunden (zwischen den Checks)
ALERT_EMAIL = "admin@example.com"  # Empfänger für Warnungen (optional)

# ---------------------------
# Hilfsfunktionen
# ---------------------------

def get_system_metrics():
    """Erfasst CPU-, RAM- und Festplattennutzung."""
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    process_count = len(psutil.pids())

    return {
        "cpu": cpu_usage,
        "memory": memory.percent,
        "disk": disk.percent,
        "processes": process_count
    }

def send_alert(subject, message):
    """(Optional) Sendet eine Warnung per E-Mail."""
    try:
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = "monitor@server"
        msg["To"] = ALERT_EMAIL

        # Lokaler Mailserver oder Dummy-Setup
        with smtplib.SMTP("localhost") as server:
            server.send_message(msg)
        print(f"⚠️  Alert sent: {subject}")
    except Exception as e:
        print(f"Fehler beim Senden der E-Mail: {e}")

def check_thresholds(metrics):
    """Prüft, ob die Systemwerte Grenzwerte überschreiten."""
    alerts = []

    if metrics["cpu"] > CPU_THRESHOLD:
        alerts.append(f"Hohe CPU-Auslastung: {metrics['cpu']}%")
    if metrics["memory"] > MEMORY_THRESHOLD:
        alerts.append(f"Hoher Speicherverbrauch: {metrics['memory']}%")
    if metrics["disk"] > DISK_THRESHOLD:
        alerts.append(f"Wenig Speicherplatz: {metrics['disk']}% belegt")

    return alerts

# ---------------------------
# Hauptfunktion
# ---------------------------

def main():
    print(f"Server-Monitor gestartet ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")

    metrics = get_system_metrics()
    print(f"CPU: {metrics['cpu']}%, RAM: {metrics['memory']}%, Disk: {metrics['disk']}%, Prozesse: {metrics['processes']}")

    alerts = check_thresholds(metrics)

    if alerts:
        alert_message = "\n".join(alerts)
        print(f"WARNUNG:\n{alert_message}")
        send_alert("Server Warning", alert_message)
    else:
        print("Alles im grünen Bereich.")

if __name__ == "__main__":
    main()
