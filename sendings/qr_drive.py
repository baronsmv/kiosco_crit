import os

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
    """
    Autentica con Google Drive usando OAuth 2.0.

    Returns:
        googleapiclient.discovery.Resource: Cliente autenticado de la API de Google Drive.
    """
    creds = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            logger.info("Access token renovado automáticamente")
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(cred_path), SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as f:
            f.write(creds.to_json())
            logger.info(f"Token guardado en: {token_path}")

    return build("drive", "v3", credentials=creds)


SERVICE = authenticate_drive()


def upload_file(file_path: str, service: Resource = SERVICE) -> str:
    """
    Sube un archivo a Google Drive y genera un enlace compartido.

    Args:
        service (Resource): Cliente autenticado de Google Drive.
        file_path (str): Ruta del archivo local.

    Returns:
        str: URL del archivo subido en Google Drive.
    """
    file_name = os.path.basename(file_path)
    media = MediaFileUpload(file_path, resumable=True)
    meta = {"name": file_name}
    resultado = (
        service.files()
        .create(body=meta, media_body=media, fields="id")
        .execute()
    )
    file_id = resultado.get("id")

    service.permissions().create(
        fileId=file_id, body={"type": "anyone", "role": "reader"}
    ).execute()

    url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
    logger.info(f"Subido: {file_name}")
    logger.info(f"Enlace: {url}")
    return url


def generate_qr(url: str, output_path: str) -> None:
    """
    Genera un código QR para un enlace y lo guarda como imagen.

    Args:
        url (str): URL a codificar en el QR.
        output_path (str): Ruta donde guardar la imagen QR.
    """
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    logger.info(f"QR guardado: {output_path}")
