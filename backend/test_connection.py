from app.config.database import engine

try:
    with engine.connect() as connection:
        print("=" * 50)
<<<<<<< HEAD
        print("Conexión exitosa con PostgreSQL")
=======
        print("✅ Conexión exitosa con PostgreSQL")
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
        print("Base de datos conectada correctamente")
        print("=" * 50)

except Exception as e:
    print("=" * 50)
<<<<<<< HEAD
    print("Error al conectar con PostgreSQL")
=======
    print("❌ Error al conectar con PostgreSQL")
>>>>>>> a9d292cd55282d2a8b29a8837da25c88e549fd12
    print(e)
    print("=" * 50)