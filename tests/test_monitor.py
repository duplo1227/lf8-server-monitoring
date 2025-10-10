import sys
import os
import psutil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.monitor import get_system_metrics

def test_metrics_return_values():
    cpu, mem, disk, proc = get_system_metrics()
    assert 0 <= cpu <= 100
    assert 0 <= mem <= 100
    assert 0 <= disk <= 100
    assert 0 <= proc <= 190
