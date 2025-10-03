# ClearNews
AI powered detection software for fake news


# Actividad 4 - Aplicación de patrón de diseño Python

## Refactor de autenticación con Patrones de Diseño

Se implementaron mejoras en la app **accounts** que se encarga del login y el singup, aplicando patrones de diseño para hacer el código más limpio, escalable y fácil de mantener.  

---

## Cambios realizados

### 1. Patrón **Factory Method**
- Archivo creado: `accounts/factories.py`  
- Se creó la clase `UserFactory` para centralizar la creación de usuarios.  
- Antes, la vista `signup_view` llamaba directamente a `User.objects.create_user`.  
- Ahora, la creación pasa por `UserFactory.create_user()`.  

**Beneficios:**
- Desacopla la lógica de creación de usuarios de las vistas.  
- Facilita añadir **roles** o validaciones adicionales sin tocar `views.py`.  

---

### 2. Patrón **Facade**
- Archivo creado: `accounts/services/auth_service.py`  
- Se creó la clase `AuthService`, que funciona como **fachada** de autenticación:  

  - `signup(request, username, password1, password2)`  
  - `signin(request, username, password)`  
  - `signout(request)`  

- Las vistas (`signup_view`, `login_view`, `logout_view`) ahora delegan en `AuthService`.  

**Beneficios:**
- Centraliza toda la lógica de autenticación en un solo archivo.  
- Vistas más limpias, enfocadas solo en la interacción con el usuario.  
- Facilita el mantenimiento: si cambia la autenticación, solo se modifica `AuthService`.  

---

### 3. Refactor de `views.py`
- Archivo modificado: `accounts/views.py`  
- Las funciones `signup_view`, `login_view` y `logout_view` fueron simplificadas para usar `AuthService`.  

**Beneficios:**
- Las vistas siguen el principio de **Single Responsibility**.  
- Código más claro y con menos duplicación.  

---

### 4. Cambios en HTML y URLs
- Código más limpio y desacoplado, las vistas no contienen lógica de negocio.
- Escalabilidad, ahora es más fácil añadir roles, validaciones o nuevas formas de login.
- Mantenibilidad, la lógica de autenticación está concentrada en `AuthService`.
- Buenas prácticas, se aplican patrones de diseño reconocidos (Factory Method y Facade), alineando el proyecto con principios de arquitectura limpia.
