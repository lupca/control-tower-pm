import os
import signal
import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import CurrentMessage

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_broker = RedisBroker(url=redis_url)
redis_broker.add_middleware(CurrentMessage())
dramatiq.set_broker(redis_broker)


def shutdown_handler(signum, frame):
    """Handle SIGTERM for graceful shutdown."""
    broker = dramatiq.get_broker()
    if hasattr(broker, "join"):
        broker.join(timeout=30000)  # 30s grace period


try:
    signal.signal(signal.SIGTERM, shutdown_handler)
except (ValueError, AttributeError):
    pass
