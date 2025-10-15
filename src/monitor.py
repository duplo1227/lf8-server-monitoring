import sys
import os
import argparse
import configparser
from datetime import datetime
import time
import psutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import alarm

def read_config(path: str):
    cfg = configparser.ConfigParser()
    cfg.read(path, encoding="utf-8")
    return cfg

def get_metrics():
    users = sorted({u.name for u in psutil.users()})
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
        "processes": len(psutil.pids()),
        "users": users,
    }

def main():
    parser = argparse.ArgumentParser(
        description="Einfaches Server-Monitoring mit zweistufigem Alarmsystem."
    )
    parser.add_argument("-c", "--config", default="config.ini", help="Pfad zur INI-Datei")
    args = parser.parse_args()

    cfg = read_config(args.config)
    mcfg = cfg["monitoring"]
    lcfg = cfg["limits"]
    scfg = cfg["smtp"]

    # Logging initialisieren
    alarm.setup_logging(mcfg.get("log_file", "logger.log"))

    interval = int(mcfg.get("interval_seconds", 30))

    # Limits lesen (als float/int)
    limits = {
        "cpu": (float(lcfg.get("cpu_soft", 80)), float(lcfg.get("cpu_hard", 95))),
        "memory": (float(lcfg.get("memory_soft", 80)), float(lcfg.get("memory_hard", 95))),
        "disk": (float(lcfg.get("disk_soft", 80)), float(lcfg.get("disk_hard", 95))),
        "processes": (float(lcfg.get("processes_soft", 180)), float(lcfg.get("processes_hard", 250))),
    }

    a = 4
    while a > 0:
        a -= 1
        data = get_metrics()
        print(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"CPU: {data['cpu']}%, RAM: {data['memory']}%, Disk: {data['disk']}%, "
            f"Prozesse: {data['processes']}, Benutzer: {len(data['users'])} {data['users']}"
        )

        if data["users"]:
            user_line = f"Aktive Benutzer: {len(data['users'])} [{', '.join(data['users'])}]"
        else:
            user_line = "Aktive Benutzer: 0 [-]"

        alarm.logging.info(user_line)

        alarm.check_and_alert("cpu", data["cpu"], *limits["cpu"], smtp_cfg=scfg, unit="%")
        alarm.check_and_alert("memory", data["memory"], *limits["memory"], smtp_cfg=scfg, unit="%")
        alarm.check_and_alert("disk", data["disk"], *limits["disk"], smtp_cfg=scfg, unit="%")
        alarm.check_and_alert("processes", data["processes"], *limits["processes"], smtp_cfg=scfg, unit="")

        time.sleep(interval)



if __name__ == "__main__":
    main()
