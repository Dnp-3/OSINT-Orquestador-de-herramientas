# modules/breach_check.py
import os
import requests
import time

# Intenta leer la API key de HIBP desde variable de entorno HIBP_API_KEY
HIBP_API_KEY = os.getenv("HIBP_API_KEY")

def check_breach(identifier):
    """
    identifier: email o username
    Verifica si un email/usuario aparece en brechas conocidas mediante HaveIBeenPwned.
    Retorna una lista de strings con los resultados.
    """
    results = []

    if not HIBP_API_KEY:
        results.append("HIBP API key no configurada. Ejecutando modo demo (sin consultas reales).")
        results.append(f"Nota: para habilitar consultas reales, exporta HIBP_API_KEY en las variables de entorno.")
        results.append(f"Simulación: No se encontraron brechas para '{identifier}' (modo demo).")
        return results

    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{identifier}"
    headers = {
        'User-Agent': 'DataOrchestrator',
        'hibp-api-key': HIBP_API_KEY,
        'Accept': 'application/json'
    }
    params = {'truncateResponse': 'false'}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        time.sleep(1.6)         # Cumplir rate limit de la API

        if resp.status_code == 200:
            breaches = resp.json()
            if not breaches:
                results.append(" [✓] No se encontraron brechas.")

            else:
                for b in breaches:
                    name = b.get('Name') or b.get('Title') or b.get('name')
                    date = b.get('BreachDate') or b.get('breachDate')
                    desc = b.get('Description', '')
                    results.append(f"- Breach: {name} | Date: {date}")
                    if desc:
                        # acortar descripcion
                        results.append(f"  Description: {desc[:200]}{'...' if len(desc) > 200 else ''}")

        elif resp.status_code == 404:
            results.append(" [✓] No se encontraron brechas (HTTP 404).")

        else:
            results.append(f" [!] Error HIBP: HTTP {resp.status_code} - {resp.text}")

    except Exception as e:
        results.append(f" [!] Excepción durante consulta HIBP: {e}")

    return results
