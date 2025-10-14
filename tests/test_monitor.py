import sys
import os
import psutil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.alarm import *
from src.monitor import get_metrics

def test_metrics_return_values():
    a = get_metrics()
    assert 0 <= a['cpu'] <= 100
    assert 0 <= a['memory'] <= 100
    assert 0 <= a['disk'] <= 100
    assert 0 <= a['processes'] <= 190
