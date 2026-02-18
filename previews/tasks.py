import os
from datetime import datetime, timedelta
from pathlib import Path

from celery import shared_task
from django.conf import settings


@shared_task
def clean_old(days: int = 30) -> str:
    """
    Delete local media files older than `days` in configured folders.
    """
    media_root = Path(settings.MEDIA_ROOT)
    folders = os.getenv("CLEAN_FOLDERS", "pdf,excel").split(",")
    cutoff_time = datetime.now() - timedelta(days=days)

    deleted = []

    for folder_name in folders:
        folder = media_root / folder_name

        if not folder.exists():
            continue

        for file in folder.glob("*"):
            if file.is_file():
                file_mtime = datetime.fromtimestamp(file.stat().st_mtime)
                if file_mtime < cutoff_time:
                    file.unlink()
                    deleted.append(str(file))

    return f"Deleted {len(deleted)} files older than {days} days"
