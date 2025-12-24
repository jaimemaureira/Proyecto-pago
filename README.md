# Pago Auto

## Conexión Flask ↔ Supabase Postgres

La app usa SQLAlchemy para conectar con la base de datos de Supabase.

### Variables de entorno
- `SUPABASE_DB_URL`: cadena de conexión Postgres de Supabase.
	- Formato: `postgres://postgres:<password>@<host>:5432/postgres`
- `SECRET_KEY`: clave de sesión Flask.
- Opcional (para usar el cliente REST de Supabase):
	- `SUPABASE_URL`
	- `SUPABASE_ANON_KEY`
	- `SUPABASE_SERVICE_ROLE_KEY`

Puedes crear un archivo `.env` en la raíz con estas variables.

### Instalación

```
pip install -r requirements.txt
```

### Ejecutar

```
python run.py
```

Prueba la conexión visitando `http://localhost:5000/db-ping`.

