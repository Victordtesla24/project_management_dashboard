import time
from functools import lru_cache


@lru_cache(maxsize=100)
def get_cached_metrics(metric_name: str, timeout: int = 60):
    # Implementation
    pass
