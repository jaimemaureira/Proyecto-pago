import os
import uuid
from werkzeug.utils import secure_filename
from supabase import create_client


def _client():
    # Debe ser el Project URL de Supabase (https://xxxxx.supabase.co)
    url = os.getenv("SUPABASE_URL", "").strip()
    key = (os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY") or "").strip()

    if not url or not key:
        raise RuntimeError("Faltan SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY/ANON_KEY")

    if not url.endswith("/"):
        url += "/"
        
    return create_client(url, key)


def upload_to_bucket(file_storage, bucket: str, path_prefix: str = "") -> str:
    client = _client()
    filename = secure_filename(file_storage.filename)
    unique = f"{uuid.uuid4()}_{filename}"
    path = f"{path_prefix}/{unique}" if path_prefix else unique

    file_storage.stream.seek(0)
    data = file_storage.read()
    content_type = file_storage.mimetype or "application/octet-stream"

    res = client.storage.from_(bucket).upload(
        path,
        data,
        file_options={"content-type": content_type, "upsert": "false"},
    )

    if isinstance(res, dict) and res.get("error"):
        raise RuntimeError(f"Supabase upload error: {res['error']}")

    return client.storage.from_(bucket).get_public_url(path)