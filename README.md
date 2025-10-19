# OSINT Data Orchestrator

**OSINT Data Orchestrator** es una herramienta modular de recolección de información que permite realizar tareas básicas de inteligencia de fuentes abiertas (OSINT) sobre diferentes tipos de datos: correos electrónicos, nombres de usuario, dominios y más.

## Características principales
- Verificación de **brechas de datos** mediante `Have I Been Pawned`.  
- Búsqueda de **nombres de usuario** en múltiples redes sociales.  
- Integración con `Sherlock` para búsqueda OSINT avanzada de usernames.  
- Consultas de **WHOIS** y registros DNS para dominios.  
- Sistema de reporte automático con guardado en archivos por módulo.  
- Diseño modular para agregar fácilmente nuevas fuentes OSINT.

---

## Requisitos
- Python 3.8+
- Módulos:
  - `requests`
  - `dnspython`
  - `python-whois`
- Herramienta externa opcional: [`sherlock`](https://github.com/sherlock-project/sherlock)

---

## Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/Dnp-3/OSINT-Orquestador-de-herramientas
   cd OSINT-Orquestador-de-herramientas
