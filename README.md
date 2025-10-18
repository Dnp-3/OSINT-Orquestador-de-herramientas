# OSINT Modular Tool (Ética)

Herramienta de recopilación OSINT modular, extensible y automatizable. Solo para uso ético y con consentimiento explícito.

## Funcionalidades

- Entrada por: nombre, email, username, número de teléfono o dominio.
- Módulos:
  - HaveIBeenPwned (con o sin API key)
  - Verificación de usernames en múltiples redes
  - WHOIS, DNS y metadatos de dominios
  - Integración con herramientas externas como `theHarvester`
- Exporta resultados en JSON, HTML y PDF

##  Instalación

```bash
git clone https://github.com/Dnp-3/OSINT-Orquestador-de-herramientas
cd OSINT-Orquestador-de-herramientas
pip install -r requirements.txt
```
## Uso
Soporta inputs: --name, --email, --username, --phone, --domain
```bash
python osint_modular_ext.py --domain example.com --consent --html --pdf
python osint_modular_ext.py --domain example.com --consent --external-cmd "theHarvester -d {domain} -b all -l 200 -f {outbase}"
```
