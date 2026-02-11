from datetime import datetime, timedelta, UTC

from celery import shared_task
from googleapiclient.discovery import Resource

from sendings.qr_drive import SERVICE
from utils.logger import get_logger

logger = get_logger(__name__)


@shared_task
def clean_old_drive(days: int = 30, service: Resource = SERVICE):
    cutoff_date = datetime.now(UTC) - timedelta(days=days)
    cutoff_rfc3339 = cutoff_date.isoformat() + "Z"

    query = f"modifiedTime < '{cutoff_rfc3339}'"
    results = (
        service.files().list(q=query, fields="files(id, name, modifiedTime)").execute()
    )

    files = results.get("files", [])
    for f in files:
        try:
            service.files().delete(fileId=f["id"]).execute()
            logger.info(f"Deleted: {f['name']} ({f['id']})")
        except Exception as e:
            logger.error(f"Error deleting {f['name']}: {e}")
