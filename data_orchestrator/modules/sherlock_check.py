# modules/sherlock_check.py
import subprocess
import shutil

def sherlock_check(username):
    """
    Ejecuta Sherlock desde CLI y devuelve su salida como lista de strings.
    Requiere tener 'sherlock' instalado globalmente (pipx o pip).
    """
    results = []

    sherlock_path = shutil.which("sherlock")
    if not shutil.which("sherlock"):
        return [
            "[ERROR] Sherlock no está instalado o no se encuentra en el PATH.",
            "Sugerencia: instala con 'pipx install sherlock' o 'pip install sherlock'.",
            "Si ya lo tienes, asegúrate de ejecutar 'pipx ensurepath'."
            ]

    try:
        process = subprocess.run(
            ["sherlock", username, "--timeout", "10", "--print-found"],
            capture_output=True,
            text=True,
            check=False,
            timeout=300 # Tiempo máximo total de Sherlock
        )

        stdout = process.stdout.strip()
        stderr = process.stderr.strip()

        if process.returncode == 0:
            if stdout:
                results.append(f"[+] Resultados de Sherlock para '{username}':")
                results += stdout.splitlines()
                results.append(f"[✓] Fin de resultados para '{username}'.")
            else:
                results.append(f"[✓] Sherlock ejecutado correctamente, pero no se encontraron coincidencias para '{username}'.")
        else:
            results.append(f"[!] Sherlock retornó código de salida {process.returncode}.")
            if stderr:
                results.append("Salida de error:")
                results += stderr.splitlines()

    except subprocess.TimeoutExpired:
        results.append(f"[ERROR] Sherlock superó el tiempo límite (timeout global alcanzado).")
    except FileNotFoundError:
        results.append("[ERROR] Sherlock no está instalado o no se encuentra en el PATH.")
    except Exception as e:
        results.append(f"[ERROR] Excepción inesperada durante ejecución de Sherlock: {e}")

    return results
