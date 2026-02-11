import json
from pathlib import Path

import requests
from celery import shared_task
from django.conf import settings

from queries.apis.views import api_espacios_disponibles


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={"max_retries": 5},
)
def fetch_espacios(direct: bool = True) -> str:
    output_file = Path(settings.BASE_DIR) / "static/data/espacios_disponibles.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_file = output_file.with_suffix(".tmp")

    if direct:
        data = api_espacios_disponibles(request=None)
    else:
        api_url = "http://django:8000/api/espacios/disponibles/"
        resp = requests.get(api_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

    with open(tmp_file, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp_file.replace(output_file)

    return f"Espacios actualizados at {output_file}"
