import os
from pathlib import Path

import qrcode
from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.http import MediaFileUpload

from utils.logger import get_logger

logger = get_logger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

cred_path = settings.GOOGLE_DRIVE_CREDENTIALS
token_path = settings.GOOGLE_DRIVE_TOKEN


def authenticate_drive() -> Resource:
    creds = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            logger.info("Access token renovado automáticamente")
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(cred_path), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as f:
            f.write(creds.to_json())
            logger.info(f"Token guardado en: {token_path}")

    return build("drive", "v3", credentials=creds)


def get_or_create_folder(folder_name: str, service: Resource) -> str:
    query = (
        f"name = '{folder_name}' "
        "and mimeType = 'application/vnd.google-apps.folder' "
        "and trashed = false"
    )

    response = (
        service.files()
        .list(
            q=query,
            spaces="drive",
            fields="files(id, name)",
        )
        .execute()
    )

    folders = response.get("files", [])

    if folders:
        return folders[0]["id"]

    # Crear carpeta si no existe
    file_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }

    folder = service.files().create(body=file_metadata, fields="id").execute()

    logger.info(f"Carpeta creada: {folder_name}")
    return folder["id"]


def upload_file(file_path: str, folder_name: str) -> str:
    service = authenticate_drive()
    file_name = os.path.basename(file_path)
    folder_id = get_or_create_folder(folder_name, service)
    media = MediaFileUpload(file_path, resumable=True)
    meta = {
        "name": file_name,
        "parents": [folder_id],
    }
    resultado = (
        service.files().create(body=meta, media_body=media, fields="id").execute()
    )
    file_id = resultado.get("id")

    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()

    url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"

    logger.info(f"Subido: {file_name} a carpeta {folder_name}")
    logger.info(f"Enlace: {url}")

    return url


def generate_qr(url: str, output_path: Path) -> None:
    """
    Genera un código QR para un enlace y lo guarda como imagen.

    Args:
        url (str): URL a codificar en el QR.
        output_path (Path): Ruta donde guardar la imagen QR.
    """
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    logger.info(f"QR guardado: {output_path}")
