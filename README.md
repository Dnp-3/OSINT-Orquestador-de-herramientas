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
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

4. Configurar variables de entorno para APIs (si usas HaveIBeenPwned o URLs personalizadas)
```powershell
$env:HIBP_API_KEY = "tu_api_key_hibp"
# (Opcional) Cambiar plataformas sociales:
$env:SOCIAL_PLATFORMS = "https://twitter.com/{},https://github.com/{}"
```

5. Ejecutar el programa
Interactivo:
```powershell
python main2.py
```
No interactivo (ejemplo):
```powershell
echo "username`nmyuser" | python main.py
```

6. Salida
- El resultado se guarda en la carpeta de reportes, la cual genera distintas carpetas y txt dependiendo de la funcionalidad que ejecutes y también se muestra en pantalla.

7. Personalización
- Cuando tengas nuevas URLs o APIs, indícalo y se integrarán en los módulos correspondientes.

---

Si tienes errores de dependencias, ejecuta:
```powershell
python -m pip install requests dnspython python-whois
```

