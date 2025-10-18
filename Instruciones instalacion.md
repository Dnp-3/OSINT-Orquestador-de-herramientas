# Data Orchestrator (local)

Instrucciones rápidas para ejecutar búsquedas reales y configurar APIs.

1) Crear un entorno virtual (recomendado):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2) Instalar dependencias:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3) Configurar variables de entorno necesarias (ejemplo HIBP):

```powershell
$env:HIBP_API_KEY = 'tu_hibp_api_key_aqui'
# Opcional: cambiar plataformas por defecto
$env:SOCIAL_PLATFORMS = 'https://twitter.com/{},https://github.com/{}'
```

4) Ejecutar:

```powershell
python main.py
```

O bien no interactivo:

```powershell
echo "username`nmyuser" | python main.py
```

5) Cuando me facilites las URLs/APIs concretas que quieres usar, actualizaré los módulos para integrarlas y añadiré ejemplos de configuración y pruebas.
