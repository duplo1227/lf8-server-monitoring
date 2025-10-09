import psutil
import time
import logging
from datetime import datetime

CPU_THRESHOLD = 30 
MEMORY_THRESHOLD = 30 
DISK_THRESHOLD = 30
CHECK_INTERVAL = 30 

logging.basicConfig(
    filename="/opt/monitoring/lf8-server-monitoring/logger.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# track CPU, RAM, disk usage and processes.
def get_system_metrics():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    process_count = len(psutil.pids())

    return cpu_usage, memory, disk, process_count

# check whether the system values ​​exceed limits
def check_thresholds(metrics):
    alerts = []

    if metrics["cpu"] > CPU_THRESHOLD:
        alerts.append(f"!!! Hohe CPU-Auslastung: {metrics['cpu']}%")
    if metrics["memory"] > MEMORY_THRESHOLD:
        alerts.append(f"!!! Hoher Speicherverbrauch: {metrics['memory']}%")
    if metrics["disk"] > DISK_THRESHOLD:
        alerts.append(f"!!! Wenig Speicherplatz: {metrics['disk']}% belegt")

    return alerts

# main function
def main():
    logging.info(f"Server Monitoring gestartet ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    metrics = get_system_metrics()
    print(f"CPU: {metrics['cpu']}%, RAM: {metrics['memory']}%, Disk: {metrics['disk']}%, Prozesse: {metrics['processes']}")
    logging.info(f"CPU: {metrics['cpu']}%, RAM: {metrics['memory']}%, Disk: {metrics['disk']}%, Prozesse: {metrics['processes']}")

    alerts = check_thresholds(metrics)

    if alerts:
        print("WARNUNG:")
        for a in alerts:
            logging.warning(a)
            print(f"- {a}")
    else:
        print("Alles gut Dolbobob.")
        logging.info("Alles im grünen Bereich.")

if __name__ == "__main__":
    while True:
        print(f"Server Monitoring gestartet ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        main()
        time.sleep(CHECK_INTERVAL)

