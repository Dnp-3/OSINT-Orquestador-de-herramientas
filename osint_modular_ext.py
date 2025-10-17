#!/usr/bin/env python3
"""
osint_modular_ext.py -- Herramienta OSINT modular (ética) con integración externa CLI
Soporta inputs: --name, --email, --username, --phone, --domain
Módulos incluidos:
 - HaveIBeenPwnedModule (opcional API key)
 - UsernameCheckModule (comprobación en múltiples sitios)
 - DomainModule (WHOIS, DNS, HTTP meta)
 - ExternalCLIModule (integra herramientas externas por línea de comandos; por defecto intenta theHarvester para domain)
Salida: JSON (siempre), HTML (opcional) y PDF (opcional, intenta wkhtmltopdf o weasyprint)
USO:
  python osint_modular_ext.py --domain example.com --consent --html --pdf
  python osint_modular_ext.py --domain example.com --consent --external-cmd "theHarvester -d {domain} -b all -l 200 -f {outbase}"
"""

import argparse
import json
import time
import os
import sys
import hashlib
import shutil
import subprocess
import re
from typing import Dict, Any, Optional, List

import requests
from bs4 import BeautifulSoup

# Optional dependencies
try:
    import whois as whoislib
except Exception:
    whoislib = None

try:
    import dns.resolver
except Exception:
    dns = None

try:
    import phonenumbers
except Exception:
    phonenumbers = None

# Optional PDF
try:
    from weasyprint import HTML as WeasyHTML
except Exception:
    WeasyHTML = None

# ---------------- Config ----------------
USER_AGENT = "osint-modular-ext/1.0 (+https://example.org)"
DELAY = 1.0
TIMEOUT = 10
OUTPUT_DIR = "osint_reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------- Module base ----------------
class ModuleBase:
    name: str = "base"
    def __init__(self, context: Dict[str, Any]):
        self.context = context
    def run(self) -> Dict[str, Any]:
        raise NotImplementedError

MODULES: Dict[str, type] = {}
def register_module(cls):
    MODULES[cls.name] = cls
    return cls

# ---------------- Modules (HaveIBeenPwned, UsernameCheck, Domain) ----------------

@register_module
class HaveIBeenPwnedModule(ModuleBase):
    name = "haveibeenpwned"
    def run(self):
        out = {"note": None, "breaches": None}
        email = self.context.get("email")
        hibp_key = self.context.get("config", {}).get("hibp_api_key")
        if not email:
            out["note"] = "No se proporcionó email; omitiendo HIBP."
            return out
        if not hibp_key:
            out["note"] = ("No HIBP API key; consulte manualmente: "
                           f"https://haveibeenpwned.com/unifiedsearch/{email}")
            return out
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        headers = {"hibp-api-key": hibp_key, "user-agent": USER_AGENT, "accept": "application/json"}
        try:
            r = requests.get(url, headers=headers, timeout=TIMEOUT)
            if r.status_code == 200:
                out["breaches"] = r.json()
            elif r.status_code == 404:
                out["breaches"] = []
            else:
                out["note"] = f"HIBP HTTP {r.status_code}"
        except Exception as e:
            out["note"] = f"Error calling HIBP: {e}"
        time.sleep(DELAY)
        return out

@register_module
class UsernameCheckModule(ModuleBase):
    name = "username_check"
    SITES = {
        "github": "https://github.com/{u}",
        "twitter": "https://twitter.com/{u}",
        "instagram": "https://www.instagram.com/{u}/",
        "reddit": "https://www.reddit.com/user/{u}",
        "keybase": "https://keybase.io/{u}"
    }
    def run(self):
        username = self.context.get("username")
        out = {"checked": [], "note": None}
        if not username:
            out["note"] = "No username provided; skipping."
            return out
        headers = {"User-Agent": USER_AGENT}
        results = []
        for name, pattern in self.SITES.items():
            url = pattern.format(u=username)
            try:
                r = requests.head(url, headers=headers, allow_redirects=True, timeout=TIMEOUT)
                if r.status_code >= 400:
                    r = requests.get(url, headers=headers, allow_redirects=True, timeout=TIMEOUT)
                exists = r.status_code in (200,301,302)
                results.append({"site": name, "url": url, "http_status": r.status_code, "exists_guess": exists})
            except Exception as e:
                results.append({"site": name, "url": url, "error": str(e)})
            time.sleep(DELAY)
        out["checked"] = results
        return out

@register_module
class DomainModule(ModuleBase):
    name = "domain_info"
    def _whois(self, domain):
        if whoislib is None:
            return {"note": "python-whois not installed; skipping WHOIS"}
        try:
            w = whoislib.whois(domain)
            try:
                return dict(w)
            except Exception:
                return str(w)
        except Exception as e:
            return {"error": str(e)}
    def _dns(self, domain):
        if dns is None:
            return {"note": "dnspython not installed; skipping DNS"}
        stats = {}
        try:
            resolver = dns.resolver.Resolver()
            for q in ("A","MX","NS","TXT"):
                try:
                    answers = resolver.resolve(domain, q, lifetime=5)
                    stats[q] = [rdata.to_text() for rdata in answers]
                except Exception as e:
                    stats[q] = f"error: {e}"
        except Exception as e:
            stats["error"] = str(e)
        return stats
    def _http_meta(self, domain):
        schemes = ["https://", "http://"]
        headers_out = {}
        meta = {}
        for s in schemes:
            url = s + domain
            try:
                r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT, allow_redirects=True)
                headers_out[url] = {"status": r.status_code, "resp_headers": dict(r.headers)}
                if r.status_code == 200 and 'text/html' in r.headers.get('Content-Type',''):
                    soup = BeautifulSoup(r.text, "html.parser")
                    title = soup.title.string.strip() if soup.title else None
                    metas = {}
                    for m in soup.find_all("meta"):
                        if m.get("name"):
                            metas[m.get("name").lower()] = m.get("content","")
                        elif m.get("property"):
                            metas[m.get("property").lower()] = m.get("content","")
                    meta[url] = {"title": title, "metas": metas}
                else:
                    meta[url] = {"note": f"status {r.status_code} or non-html"}
            except Exception as e:
                headers_out[url] = {"error": str(e)}
                meta[url] = {"error": str(e)}
            time.sleep(DELAY)
        return {"http": headers_out, "meta": meta}
    def run(self):
        domain = self.context.get("domain")
        out = {"note": None, "whois": None, "dns": None, "http_meta": None}
        if not domain:
            out["note"] = "No domain provided; skipping domain module."
            return out
        out["whois"] = self._whois(domain)
        out["dns"] = self._dns(domain)
        out["http_meta"] = self._http_meta(domain)
        return out

# ---------------- External CLI Integration Module ----------------
@register_module
class ExternalCLIModule(ModuleBase):
    """
    Ejecuta una herramienta externa configurable (comando), captura salida cruda y parsea
    correos y hosts mediante regex. NO instala ni llama APIs externas por sí misma.
    Config: context['config']['external_cmd'] -> string template (puede contener placeholders:
            {domain}, {email}, {username}, {outbase})
    Ejemplo por defecto para domain: "theHarvester -d {domain} -b all -l 200 -f {outbase}"
    """
    name = "external_cli"

    EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", re.IGNORECASE)
    HOST_REGEX = re.compile(r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b", re.IGNORECASE)

    def _run_cmd(self, cmd_list, capture_file=None):
        try:
            # run and capture stdout+stderr
            proc = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300, text=True)
            output = proc.stdout
            # optionally read capture_file output (if the command wrote files)
            if capture_file and os.path.exists(capture_file):
                try:
                    with open(capture_file, "r", encoding="utf-8", errors="ignore") as fh:
                        captured = fh.read()
                    output = (output or "") + "\n\n--captured-file--\n\n" + captured
                except Exception:
                    pass
            return {"cmd": " ".join(cmd_list), "returncode": proc.returncode, "output": output}
        except FileNotFoundError as e:
            return {"error": f"command not found: {cmd_list[0]}"}
        except subprocess.TimeoutExpired as e:
            return {"error": "command timeout"}
        except Exception as e:
            return {"error": str(e)}

    def _parse_artifacts(self, text):
        emails = set(self.EMAIL_REGEX.findall(text or ""))
        hosts = set(self.HOST_REGEX.findall(text or ""))
        # try to remove trivial matches like "com" or ip fragments by simple filter
        hosts = {h for h in hosts if len(h) > 3 and not h.isdigit()}
        return {"emails": sorted(emails), "hosts": sorted(hosts)}

    def run(self):
        cfg = self.context.get("config", {})
        cmd_template = cfg.get("external_cmd")
        domain = self.context.get("domain")
        email = self.context.get("email")
        username = self.context.get("username")

        out = {"note": None, "executed": None, "parsed": None}
        if not cmd_template:
            # default behaviour: if domain provided try theHarvester (if installed)
            if domain:
                outbase = os.path.join(OUTPUT_DIR, f"theharvester_{int(time.time())}")
                # default command tries to produce some file; many installs produce .xml/.html; we will check for outbase + '*'
                cmd_template = "theHarvester -d {domain} -b all -l 200 -f {outbase}"
                cfg_cmd = cmd_template.format(domain=domain, email=email or "", username=username or "", outbase=outbase)
            else:
                out["note"] = "No external_cmd provided and no domain to run default theHarvester; skipping."
                return out
        # Fill template with placeholders
        outbase = os.path.join(OUTPUT_DIR, f"external_{int(time.time())}")
        cmd_filled = cmd_template.format(domain=domain or "", email=email or "", username=username or "", outbase=outbase)
        # split command (simple split; for complex commands, pass as list in config)
        cmd_list = cmd_filled.strip().split()
        # run
        res = self._run_cmd(cmd_list, capture_file=outbase + ".xml")
        out["executed"] = res
        # parse artifacts from captured output
        parsed = self._parse_artifacts(res.get("output") if isinstance(res, dict) else None)
        out["parsed"] = parsed
        # try to look for files produced (like outbase.html, outbase.xml)
        produced = []
        for ext in (".html", ".xml", ".json", ".txt"):
            p = outbase + ext
            if os.path.exists(p):
                produced.append(p)
        if produced:
            out["produced_files"] = produced
        time.sleep(DELAY)
        return out

# ---------------- Core runner ----------------
def run_all(context: Dict[str, Any], selected_modules: Optional[List[str]] = None) -> Dict[str, Any]:
    report = {"generated_at": time.ctime(), "inputs": context, "modules": {}}
    modules_to_run = selected_modules or list(MODULES.keys())
    for mod_name in modules_to_run:
        cls = MODULES.get(mod_name)
        if not cls:
            report["modules"][mod_name] = {"error": "module not registered"}
            continue
        try:
            m = cls(context)
            report["modules"][mod_name] = m.run()
        except Exception as e:
            report["modules"][mod_name] = {"error": str(e)}
    return report

# --------------- Utilities ---------------
def sanity_checks(args) -> Optional[str]:
    if not args.consent:
        return "Consentimiento requerido (--consent). No ejecutar sin permiso."
    if not (args.name or args.email or args.username or args.phone or args.domain):
        return "Se requiere al menos uno de: --name, --email, --username, --phone, --domain"
    return None

def validate_phone(phone: str):
    if phonenumbers is None:
        return {"note": "phonenumbers not installed; not validated", "raw": phone}
    try:
        p = phonenumbers.parse(phone, None)
        valid = phonenumbers.is_possible_number(p) or phonenumbers.is_valid_number(p)
        return {"e164": phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.E164), "valid_guess": valid}
    except Exception as e:
        return {"error": str(e), "raw": phone}

def save_report(report: Dict[str, Any], outname: Optional[str] = None, as_html: bool = False, as_pdf: bool = False) -> Dict[str, str]:
    ts = int(time.time())
    outname = outname or f"osint_report_{ts}.json"
    outpath = os.path.join(OUTPUT_DIR, outname)
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    results = {"json": outpath}
    if as_html:
        htmlpath = outpath.replace(".json", ".html")
        with open(htmlpath, "w", encoding="utf-8") as f:
            f.write(report_to_html(report))
        results["html"] = htmlpath
        if as_pdf:
            pdfpath = htmlpath.replace(".html", ".pdf")
            # try wkhtmltopdf first
            wk = shutil.which("wkhtmltopdf")
            if wk:
                try:
                    subprocess.run([wk, htmlpath, pdfpath], check=True, timeout=120)
                    results["pdf"] = pdfpath
                except Exception as e:
                    results["pdf_error"] = f"wkhtmltopdf conversion failed: {e}"
            elif WeasyHTML is not None:
                try:
                    WeasyHTML(string=open(htmlpath, "r", encoding="utf-8").read()).write_pdf(pdfpath)
                    results["pdf"] = pdfpath
                except Exception as e:
                    results["pdf_error"] = f"weasyprint conversion failed: {e}"
            else:
                results["pdf_error"] = "No wkhtmltopdf or weasyprint available; cannot generate PDF"
    return results

def report_to_html(report: Dict[str, Any]) -> str:
    html = ["<html><head><meta charset='utf-8'><title>OSINT Report</title>"
            "<style>body{font-family:Arial;margin:20px} pre{background:#f6f6f6;padding:10px;overflow:auto} "
            "table{border-collapse:collapse;width:100%} td,th{border:1px solid #ddd;padding:6px}</style></head><body>"]
    html.append(f"<h1>OSINT Report</h1><p>Generado en: {report.get('generated_at')}</p>")
    html.append("<h2>Inputs</h2><pre>"+json.dumps(report.get("inputs", {}), indent=2, ensure_ascii=False)+"</pre>")
    html.append("<h2>Módulos</h2>")
    for name, data in report.get("modules", {}).items():
        html.append(f"<h3>{name}</h3>")
        html.append("<pre>"+json.dumps(data, indent=2, ensure_ascii=False)+"</pre>")
    html.append("</body></html>")
    return "\n".join(html)

# ----------------- CLI -----------------
def main():
    parser = argparse.ArgumentParser(description="osint_modular_ext.py -- OSINT modular con integración externa")
    parser.add_argument("--name")
    parser.add_argument("--email")
    parser.add_argument("--username")
    parser.add_argument("--phone")
    parser.add_argument("--domain")
    parser.add_argument("--consent", action="store_true")
    parser.add_argument("--hibp-key", help="HIBP API key (optional)")
    parser.add_argument("--modules", help="CSV list of modules to run (default: all)", default=None)
    parser.add_argument("--out", help="Base name for output JSON (in osint_reports/)", default=None)
    parser.add_argument("--html", action="store_true", help="Generate HTML")
    parser.add_argument("--pdf", action="store_true", help="Generate PDF (requires wkhtmltopdf or weasyprint)")
    parser.add_argument("--external-cmd", help="External CLI command template (use placeholders {domain},{email},{username},{outbase})")
    args = parser.parse_args()

    err = sanity_checks(args)
    if err:
        print("ERROR:", err)
        sys.exit(1)

    context = {
        "name": args.name,
        "email": args.email,
        "username": args.username,
        "phone": args.phone,
        "domain": args.domain,
        "config": {"hibp_api_key": args.hibp_key, "external_cmd": args.external_cmd}
    }

    if args.phone:
        context["phone_validation"] = validate_phone(args.phone)

    modules = None
    if args.modules:
        modules = [m.strip() for m in args.modules.split(",")]

    print("[*] Ejecutando módulos:", modules or list(MODULES.keys()))
    report = run_all(context, selected_modules=modules)

    print("[*] Guardando report...")
    saved = save_report(report, outname=args.out, as_html=args.html, as_pdf=args.pdf)
    print("[+] Guardado:", saved)
    print("[+] Módulos disponibles:", ", ".join(MODULES.keys()))
    print("[!] Recuerda: usa esto solo con permiso y respetando TOS")

if __name__ == "__main__":
    main()
