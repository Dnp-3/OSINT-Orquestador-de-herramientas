# input_handler.py
def get_input():
    print("Selecciona tipo de entrada:")
    print("1. Name")
    print("2. Email")
    print("3. Username")
    print("4. Username (Sherlock)")
    print("5. Phone (Próximamente)")
    print("6. Domain")
 
    options = {
        "1": "name",
        "2": "email",
        "3": "username",
        "4": "username_sherlock",
        "5": "phone",          # si aún no implementas, puedes bloquear más abajo
        "6": "domain",
    }
 
    attempts = 0
    while True:
        choice = input("\nIngresa número (1-6): ").strip()
        query_type = options.get(choice)
 
        if not query_type:
            attempts += 1
            print("[!] Opción inválida")
            if attempts >= 3:
                raise ValueError("Demasiados intentos inválidos.")
                quit()
            continue
 
        if query_type == "phone":
            print("[!] La opción 'phone' aún no está disponible.")
            continue
 
        value = input(f"Ingresa el {query_type}: ").strip()
        if not value:
            print("[!] El valor no puede estar vacío")
            continue
 
        # ÉXITO: siempre devolvemos una tupla

        return query_type, value
