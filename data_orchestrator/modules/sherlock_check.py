# modules/sherlock_check.py
import subprocess
import shutil

def sherlock_check(username):
    """
    Ejecuta Sherlock desde CLI y devuelve su salida como lista de strings.
    Requiere tener 'sherlock' instalado globalmente (pipx o pip).
    """
    results = []

    if not shutil.which("sherlock"):
        return ["[ERROR] Sherlock no está instalado o no se encuentra en el PATH."]

    try:
        process = subprocess.run(
            ["sherlock", username, "--timeout", "10", "--print-found"],
            capture_output=True,
            text=True,
            check=False
        )

        if process.returncode == 0:
            if process.stdout.strip():
                results.append("=== Sherlock Results ===")
                results += process.stdout.strip().splitlines()
            else:
                results.append("[INFO] Sherlock ejecutado, pero no se encontraron resultados.")
        else:
            results.append(f"[SHERLOCK ERROR] Código de salida: {process.returncode}")
            if process.stderr:
                results += process.stderr.strip().splitlines()

    except FileNotFoundError:
        results.append("[ERROR] Sherlock no está instalado o no se encuentra en el PATH.")
    except Exception as e:
        results.append(f"[SHERLOCK ERROR] {e}")

    return results
