from app.config.database import engine

try:
    with engine.connect() as connection:
        print("=" * 50)
        print("Conexión exitosa con PostgreSQL")
        print("Base de datos conectada correctamente")
        print("=" * 50)

except Exception as e:
    print("=" * 50)
    print("Error al conectar con PostgreSQL")
    print(e)
    print("=" * 50)