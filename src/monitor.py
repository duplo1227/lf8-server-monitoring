import sys
import os
import argparse
import configparser
from datetime import datetime
import time
import psutil

# Add parent directory to the import path so we can import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import alarm

# Read configuration values from the config.ini file
def read_config(path: str):
    cfg = configparser.ConfigParser()
    cfg.read(path, encoding="utf-8")
    return cfg


# Collect current system metrics (CPU, memory, disk, processes, users)
def get_metrics():
    users = sorted({u.name for u in psutil.users()})
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
        "processes": len(psutil.pids()),
        "users": users,
    }


# Main function: load config, start logging, and monitor system metrics
def main():
    # Read command line arguments (e.g. path to config.ini)
    parser = argparse.ArgumentParser(
        description="Simple server monitoring with a two-level alert system."
    )
    parser.add_argument("-c", "--config", default="config.ini", help="Path to the INI configuration file")
    args = parser.parse_args()

    # Load configuration sections
    cfg = read_config(args.config)
    mcfg = cfg["monitoring"]
    lcfg = cfg["limits"]
    scfg = cfg["smtp"]

    # Initialize logging
    alarm.setup_logging(mcfg.get("log_file", "logger.log"))

    # Read monitoring interval (in seconds)
    interval = int(mcfg.get("interval_seconds", 30))

    # Read threshold limits (soft/hard) from config
    limits = {
        "cpu": (float(lcfg.get("cpu_soft", 80)), float(lcfg.get("cpu_hard", 95))),
        "memory": (float(lcfg.get("memory_soft", 80)), float(lcfg.get("memory_hard", 95))),
        "disk": (float(lcfg.get("disk_soft", 80)), float(lcfg.get("disk_hard", 95))),
        "processes": (float(lcfg.get("processes_soft", 180)), float(lcfg.get("processes_hard", 250))),
    }

    # Monitoring loop (runs 4 times here, can be changed to run continuously)
    a = 4
    while a > 0:
        a -= 1

        # Get current system data
        data = get_metrics()

        # Print values to console
        print(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"CPU: {data['cpu']}%, RAM: {data['memory']}%, Disk: {data['disk']}%, "
            f"Processes: {data['processes']}, Users: {len(data['users'])} {data['users']}"
        )

        # Log information about active users
        if data["users"]:
            user_line = f"Active users: {len(data['users'])} [{', '.join(data['users'])}]"
        else:
            user_line = "Active users: 0 [-]"
        alarm.logging.info(user_line)

        # Check each metric and send alert if limits are exceeded
        alarm.check_and_alert("cpu", data["cpu"], *limits["cpu"], smtp_cfg=scfg, unit="%")
        alarm.check_and_alert("memory", data["memory"], *limits["memory"], smtp_cfg=scfg, unit="%")
        alarm.check_and_alert("disk", data["disk"], *limits["disk"], smtp_cfg=scfg, unit="%")
        alarm.check_and_alert("processes", data["processes"], *limits["processes"], smtp_cfg=scfg, unit="")

        # Wait for the next check
        time.sleep(interval)


# Entry point of the script
if __name__ == "__main__":
    main()
