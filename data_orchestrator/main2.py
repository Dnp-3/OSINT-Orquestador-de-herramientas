from input_handler import get_input
from modules import breach_check, username_check, domain_lookup, sherlock_check 
import os
from datetime import datetime, timezone

REPORT_DIR = "report"

def save_report(module_name, content_lines):
    """
    Guarda el contenido en un archivo dentro de una carpeta específica para el módulo.
    """
    # Crear carpeta report si no existe
    os.makedirs(REPORT_DIR, exist_ok=True)

    # Crear carpeta para el módulo
    module_dir = os.path.join(REPORT_DIR, module_name)
    os.makedirs(module_dir, exist_ok=True)

    # Nombre del archivo con timestamp para evitar sobreescritura
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    filename = f"result_{timestamp}.txt"
    filepath = os.path.join(module_dir, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(content_lines))
        print(f"[✓] Resultados guardados en '{os.path.abspath(filepath)}'")
    except Exception as e:
        print(f"[!] Error guardando resultados para {module_name}: {e}")

def main():
    query_type, value = get_input()
    breach_check_bool = 0
    social_media_check_bool = 0
    sherlock_check_bool = 0
    whois_lookup_bool = 0
    phone_bool = 0
    
    # Header común
    header = f"=== Data Orchestrator Result - {datetime.now(timezone.utc).isoformat()} UTC ==="
    header_lines = [
        header,
        f"Input Type: {query_type}",
        f"Value: {value}",
        ""
    ]
    
    # Breach check for email
    if query_type == 'email':
        breach_check_bool = 1
        lines = [ "[+] Breach check (HaveIBeenPwned):" ]
        lines += breach_check.check_breach(value)
        lines.append("")
        save_report("breach_check", header_lines + lines)
    
    # Name and username check across social platforms
    if query_type in ['username','name']:
        social_media_check_bool = 1
        lines = ["[+] Social media username check:"]
        lines += username_check.check_username(value)
        lines.append("")
        save_report("username_check", header_lines + lines)
    
    # Sherlock check for username
    if query_type == 'username_sherlock':
        sherlock_check_bool = 1
        lines = ["[+] Sherlock username check:"]
        lines += sherlock_check.sherlock_check(value)
        lines.append("")
        save_report("sherlock_check", header_lines + lines)
        
    # Domain and email WHOIS/DNS lookup
    if query_type in ['domain', 'email']:
        whois_lookup_bool = 1
        lines = ["[+] Domain WHOIS and DNS lookup:"]
        lines += domain_lookup.lookup_domain(value)
        lines.append("")
        save_report("whois_lookup", header_lines + lines)
    
    # If name or phone and no modules matched, note it
    if query_type == 'phone':
        phone_bool = 1
        lines = header_lines + ["No external modules configured para 'phone'. Puedes añadir módulos adicionales."]
        save_report("misc", lines)

    # También imprime todo junto en consola
    # Para eso concatenamos todos los resultados en orden
    output_lines = header_lines[:]
    if (breach_check_bool or social_media_check_bool or whois_lookup_bool or phone_bool or sherlock_check_bool):
        if breach_check_bool:
            output_lines.append("[+] Breach check (HaveIBeenPwned):")
            output_lines += breach_check.check_breach(value)
            output_lines.append("")
        elif social_media_check_bool:
            output_lines.append("[+] Social media username check:")
            output_lines += username_check.check_username(value)
            output_lines.append("")
        elif whois_lookup_bool:
            output_lines.append("[+] Domain WHOIS and DNS lookup:")
            output_lines += domain_lookup.lookup_domain(value)
            output_lines.append("")
        elif sherlock_check_bool:
            output_lines.append("[+] Sherlock username check:")
            output_lines += sherlock_check.sherlock_check(value)
            output_lines.append("")    
        elif phone_bool and len(output_lines) == 4:
            output_lines.append("No external modules configured para o 'phone'. Puedes añadir módulos adicionales.")
    else:
        output_lines.append("No external modules executed. Puedes añadir módulos adicionales.")

    print("\n".join(output_lines))

if __name__ == "__main__":
    main()
