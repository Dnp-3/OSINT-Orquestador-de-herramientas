# modules/domain_lookup.py
import socket
import dns.resolver
import whois

def lookup_domain(domain):
    """
    Realiza WHOIS y consultas DNS sencillas.
    Retorna lista de strings (no imprime).
    """
    results = []

    # WHOIS
    try:
        w = whois.whois(domain)
        results.append("WHOIS:")
        registrar = getattr(w, "registrar", None)
        creation = getattr(w, "creation_date", None)
        expiration = getattr(w, "expiration_date", None)
        nameservers = getattr(w, "name_servers", None)

        results.append(f"  Registrar: {registrar}")
        results.append(f"  Creation date: {creation}")
        results.append(f"  Expiration date: {expiration}")
        results.append(f"  Name servers: {nameservers}")
    except Exception as e:
        results.append(f"WHOIS lookup failed: {e}")

    # DNS records (A, MX, NS)
    results.append("DNS records:")
    for record_type in ['A', 'MX', 'NS']:
        try:
            answers = dns.resolver.resolve(domain, record_type, lifetime=8)
            for r in answers:
                results.append(f"  {record_type}: {r.to_text()}")
        except dns.resolver.NoAnswer:
            results.append(f"  {record_type}: No answer")
        except dns.resolver.NXDOMAIN:
            results.append(f"  {record_type}: Domain does not exist (NXDOMAIN)")
        except Exception as e:
            results.append(f"  {record_type}: Error -> {e}")

    # Reverse lookup (opcional, para primer A record)
    try:
        a_records = dns.resolver.resolve(domain, 'A', lifetime=8)
        first_ip = a_records[0].to_text()
        try:
            host = socket.gethostbyaddr(first_ip)
            results.append(f"Reverse DNS for {first_ip}: {host[0]}")
        except Exception:
            results.append(f"No reverse DNS for {first_ip} or lookup failed.")
    except Exception:
        # ya hay mensajes en la sección DNS si falla
        pass

    return results
