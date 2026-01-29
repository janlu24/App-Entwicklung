import os

# Die Liste unserer Apps
apps = [
    "core",
    "apps/users",
    "apps/ai_engine",
    "apps/sales",
    "apps/inventory",
    "apps/finance"
]

print("--- Starte Reparatur ---")

for app in apps:
    # Pfad zum migrations-Ordner bauen
    migrations_dir = os.path.join(os.getcwd(), app, "migrations")
    
    # 1. Ordner erstellen, falls er fehlt
    os.makedirs(migrations_dir, exist_ok=True)
    
    # 2. __init__.py erstellen
    init_file = os.path.join(migrations_dir, "__init__.py")
    
    # Datei schreiben (leer)
    with open(init_file, 'w') as f:
        pass 
        
    print(f"✅ OK: {init_file}")

print("--- Fertig! Versuche jetzt makemigrations ---")