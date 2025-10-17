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
git clone https://github.com/tuusuario/osint-modular.git
cd osint-modular
pip install -r requirements.txt
