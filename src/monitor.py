import psutil
import time
import logging
from datetime import datetime

CPU_THRESHOLD = 30 
MEMORY_THRESHOLD = 30 
DISK_THRESHOLD = 30
CHECK_INTERVAL = 30 
a = 5

logging.basicConfig(
    filename="/opt/monitoring/lf8-server-monitoring/logger.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# track CPU, RAM, disk usage and processes.
def get_system_metrics():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    process_count = len(psutil.pids())

    return cpu_usage, memory, disk, process_count

# check whether the system values ​​exceed limits
def check_thresholds(cpu, memory, disk):
    alerts = []

    if cpu > CPU_THRESHOLD:
        alerts.append(f"!!! Hohe CPU-Auslastung: {cpu}%")
    if memory > MEMORY_THRESHOLD:
        alerts.append(f"!!! Hoher Speicherverbrauch: {memory}%")
    if disk > DISK_THRESHOLD:
        alerts.append(f"!!! Wenig Speicherplatz: {disk}% belegt")

    return alerts

# main function
def main():
    logging.info(f"Server Monitoring gestartet ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    cpu, memory, disk, processes = get_system_metrics()
    print(f"CPU: {cpu}%, RAM: {memory}%, Disk: {disk}%, Prozesse: {processes}")
    logging.info(f"CPU: {cpu}%, RAM: {memory}%, Disk: {disk}%, Prozesse: {processes}")

    alerts = check_thresholds(cpu, memory, disk)

    if alerts:
        print("WARNUNG:")
        for a in alerts:
            logging.warning(a)
            print(f"- {a}")
    else:
        print("Alles im grünen Bereich.")
        logging.info("Alles im grünen Bereich.")

if __name__ == "__main__":
    while a > 0:
    a -= 1
    print(f"Server Monitoring gestartet ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    main()
    time.sleep(CHECK_INTERVAL)


