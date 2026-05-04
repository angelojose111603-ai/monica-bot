import os
import subprocess

if __name__ == "__main__":
    print("Iniciando el servidor de Monica...")
    print("Abre tu navegador en http://localhost:8080")
    try:
        subprocess.run(["python", "server.py"], check=True)
    except KeyboardInterrupt:
        print("\nServidor detenido.")
