import os
from supabase import create_client

def get_supabase():
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]  # SOLO backend
    return create_client(url, key)
