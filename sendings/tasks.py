from datetime import datetime, timedelta, UTC

from celery import shared_task

from sendings.qr_drive import get_or_create_folder, authenticate_drive
from utils.logger import get_logger

logger = get_logger(__name__)


@shared_task
def clean_old_drive(folder_name: str = "kiosco", days: int = 30) -> None:
    service = authenticate_drive()
    folder_id = get_or_create_folder(folder_name, service)

    cutoff_date = datetime.now(UTC) - timedelta(days=days)
    cutoff_rfc3339 = cutoff_date.isoformat().replace("+00:00", "Z")

    query = (
        f"'{folder_id}' in parents "
        f"and modifiedTime < '{cutoff_rfc3339}' "
        "and trashed = false"
    )

    page_token = None
    deleted_count = 0

    while True:
        response = (
            service.files()
            .list(
                q=query,
                fields="nextPageToken, files(id, name)",
                pageToken=page_token,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            )
            .execute()
        )

        files = response.get("files", [])

        for f in files:
            try:
                service.files().delete(
                    fileId=f["id"],
                    supportsAllDrives=True,
                ).execute()
                deleted_count += 1
                logger.info(f"Deleted: {f['name']} ({f['id']})")
            except Exception as e:
                logger.error(f"Error deleting {f['name']}: {e}")

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    if deleted_count == 0:
        logger.info(f"No old files to delete in '{folder_name}'")
    else:
        logger.info(f"Deleted {deleted_count} files from '{folder_name}'")
