from app.db.database import engine

conn = engine.connect()
print("Conexion OK")
conn.close()
