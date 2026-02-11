import os
from datetime import datetime, timedelta
from pathlib import Path

from celery import shared_task
from django.conf import settings


@shared_task
def clean_old():
    """
    Deletes PDF and Excel files older than PDF_CLEAN_MINUTES
    inside /media/pdf and /media/excel
    """

    media_root = Path(settings.MEDIA_ROOT)

    folders = os.getenv("CLEAN_FOLDERS", "pdf,excel").split(",")
    minutes = int(os.getenv("PDF_CLEAN_MINUTES", 120))
    cutoff_time = datetime.now() - timedelta(minutes=minutes)

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

    return f"Deleted {len(deleted)} files"
