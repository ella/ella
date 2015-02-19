"""
If RQ is installed, register our maintenance commands as periodic jobs to
avoid the requirement for external crond.
"""

try:
    from datetime import timedelta

    from scout.decorators import periodic_job

    from ella.core.management import generate_publish_signals, regenerate_listing_handlers

    periodic_job(run_every=timedelta(minutes=5))(generate_publish_signals)
    periodic_job(run_every=timedelta(hours=3))(regenerate_listing_handlers)
except ImportError:
    # RQ not installed
    pass

