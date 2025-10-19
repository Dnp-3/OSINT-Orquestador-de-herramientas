# OSINT Data Orchestrator

**OSINT Data Orchestrator** es una herramienta modular de recolección de información OSINT. Permite realizar tareas básicas de inteligencia de fuentes abiertas (OSINT) sobre diferentes tipos de datos: correos electrónicos, nombres de usuario, dominios y cuentas de redes sociales. Posteriormente genera reportes en **HTML** para una mejor visualización.

## Estructura del proyecto

```
  data_orchestrator/
│
├── main.py              # Script principal
├── input_handler.py     # Gestión de entradas
│
├── modules/             # Módulos independientes
│   ├── __init__.py
│   ├── breach_check.py
│   ├── username_check.py
│   ├── sherlock_check.py
│   └── domain_lookup.py
│
└── report/              # Se genera automáticamente al ejecutar consultas
```

## Características principales
- Verificación de **brechas de datos** mediante `Have I Been Pawned`.  
- Búsqueda de **nombres de usuario** en múltiples redes sociales.  
- Integración con `Sherlock` para búsqueda OSINT avanzada de usernames.  
- Consultas de **WHOIS** y registros DNS para dominios.  
- Sistema de reporte automático con guardado en archivos por módulo.  
- Diseño modular para agregar fácilmente nuevas fuentes OSINT.

---

## Requisitos
- Python 3.10+
- Librerias Python:
  - `requests`
  - `dnspython`
  - `python-whois`

- Herramienta externa opcional:
  - pipx install sherlock
  - [`sherlock`](https://github.com/sherlock-project/sherlock)

- Para consultas reales en Have I Been Pwned debes exportar tu API key
  -  Linux / macOS
         ```
         export HIBP_API_KEY="TU_API_KEY_AQUI"
         python main2.py
         ```
          
  - Windows CMD
        ```
        set HIBP_API_KEY=TU_API_KEY_AQUI
        python main.py
        ```
        
  - Windows PowerShell
       ```
        $env:HIBP_API_KEY="TU_API_KEY_AQUI"
        python main.py
       ```
---

## Instalación

1. Clonar el repositorio
```bash
git clone https://github.com/Dnp-3/OSINT-Orquestador-de-herramientas
cd OSINT-Orquestador-de-herramientas
```
2. (Opcional pero recomendado) Crear un entorno virtual
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. Instalar dependencias
```
python -m pip install --upgrade pip
python -m pip install requests
python -m pip install dnspython
python -m pip install python-whois
python -m pip install sherlock-project
```

4. Configurar variables de entorno para APIs (si usas HaveIBeenPwned o URLs personalizadas)
```powershell
$env:HIBP_API_KEY = "tu_api_key_hibp"
# (Opcional) Cambiar plataformas sociales:
$env:SOCIAL_PLATFORMS = "https://twitter.com/{},https://github.com/{}"
```

5. Ejecutar el programa principal
- ```
  cd data_orchestrator
  python main2.py
  ```

- Selecciona el tipo de entrada
- ```  
  1. Name
  2. Email
  3. Username
  4. Username (Sherlock)
  5. Phone (soon)
  6. Domain
  ```
- Escribe el valor de la entrada elegida

6. Salida
- El resultado se guarda en la carpeta de reportes, la cual genera distintas carpetas y archivos html dependiendo de la funcionalidad que ejecutes y también se muestra en pantalla.

7. Personalización
- Cuando tengas nuevas URLs o APIs, indícalo y se integrarán en los módulos correspondientes.

---
