# modules/username_check.py
import requests

# Lista básica de plataformas. Puedes agregar o quitar URLs.
SOCIAL_PLATFORMS = [
    "https://twitter.com/{}",
    "https://instagram.com/{}",
    "https://github.com/{}",
    "https://www.reddit.com/user/{}",
    "https://www.facebook.com/{}",
    "https://www.twitch.tv/{}",         # Añadido Twitch
    "https://www.youtube.com/{}",       # Añadido YouTube
]

HEADERS = {
    "User-Agent": "DataOrchestrator/1.0"
}

def check_username(username):
    """
    Revisa la existencia de un username en varias plataformas.
    Devuelve lista de strings con resultados.
    """
    results = []
    for template in SOCIAL_PLATFORMS:
        url = template.format(username)
        try:
            # use HEAD primero para ser más ligero; algunos sitios bloquean HEAD, fallback a GET
            try:
                r = requests.head(url, headers=HEADERS, allow_redirects=True, timeout=8)
                status = r.status_code
                # Algunos sitios devuelven 200 siempre; interpretar con cautela.
            except Exception:
                r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=8)
                status = r.status_code

            if status == 200:
                results.append(f"[FOUND] {url} (HTTP {status})")
            elif status == 401 or status == 403:
                results.append(f"[POTENTIAL] {url} returned HTTP {status} (acceso restringido)")
            elif status == 404:
                results.append(f"[NOT FOUND] {url} (HTTP {status})")
            else:
                results.append(f"[UNKNOWN] {url} (HTTP {status})")
        except Exception as e:
            results.append(f"[ERROR] {url} -> {e}")
    return results