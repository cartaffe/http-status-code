# Flask HTTP Status Code Server

Un servidor HTTP simple construido con Flask que demuestra diferentes códigos de estado HTTP (2xx, 3xx, 4xx, 5xx) con autenticación Bearer Token.

## Características

- ✅ Múltiples códigos de estado HTTP (200, 201, 204, 301, 302, 304, 400, 401, 403, 404, 405, 409, 410, 429, 500, 501, 503)
- 🔐 Autenticación con Bearer Token
- 🚦 Rate limiting (límite de peticiones)
- 📱 Interfaz web HTML responsive
- 🐳 Listo para Docker
- 🩺 Health check incluido

## Requisitos

### Ejecución local
- Python 3.8 o superior
- Flask 3.0.0

### Ejecución con Docker
- Docker instalado
- Docker Compose (opcional)

## Instalación

### Opción 1: Ejecución local

```bash
# Clonar o descargar el proyecto
git clone http-status-code
cd http-status-code

# Instalar dependencias
pip install flask==3.0.0

# Ejecutar el servidor
python server.py
```

El servidor estará disponible en `http://localhost:5000`

### Opción 2: Ejecución con Docker

```bash
# Construir la imagen
docker build -t http-status-code-server .

# Ejecutar el contenedor
docker run -d --name flask-server -p 5000:5000 http-status-code-server

# Ver logs
docker logs -f flask-server
```

### Opción 3: Docker Compose

```bash
# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

## Configuración

### Bearer Token

El token de autenticación por defecto es: `my-secret-token-12345`

Para usar un token personalizado, modifica la variable `VALID_TOKEN` en server.py` o usa una variable de entorno:

```bash
docker run -d -p 5000:5000 -e BEARER_TOKEN="tu-token-secreto" http-status-code-server
```

### Rate Limiting

Por defecto, el endpoint `/rate-limited` permite 5 peticiones por minuto por IP. Puedes modificar este límite con la variable de entorno `RATE_LIMIT`:

```bash
docker run -d -p 5000:5000 -e RATE_LIMIT=10 http-status-code-server
```

## Endpoints

### Códigos 2xx (Éxito)

| Endpoint | Código | Descripción |
|----------|--------|-------------|
| `/` | 200 | Página principal |
| `/success` | 200 | Respuesta exitosa |
| `/created` | 201 | Recurso creado |
| `/accepted` | 202 | Petición aceptada |
| `/no-content` | 204 | Sin contenido (sin body) |

### Códigos 3xx (Redirección)

| Endpoint | Código | Descripción |
|----------|--------|-------------|
| `/redirect-perm` | 301 | Redirección permanente |
| `/redirect-temp` | 302 | Redirección temporal |
| `/not-modified` | 304 | No modificado |

### Códigos 4xx (Errores del Cliente)

| Endpoint | Código | Descripción |
|----------|--------|-------------|
| `/bad-request` | 400 | Petición mal formada |
| `/protected` | 401 | No autorizado (requiere token) |
| `/forbidden` | 403 | Acceso prohibido |
| `/notfound` | 404 | Recurso no encontrado |
| `/method-not-allowed` | 405 | Método HTTP no permitido |
| `/conflict` | 409 | Conflicto |
| `/gone` | 410 | Recurso eliminado permanentemente |
| `/rate-limited` | 429 | Demasiadas peticiones |

### Códigos 5xx (Errores del Servidor)

| Endpoint | Código | Descripción |
|----------|--------|-------------|
| `/error` | 500 | Error interno del servidor |
| `/not-implemented` | 501 | No implementado |
| `/service-unavailable` | 503 | Servicio no disponible |

## Ejemplos de Uso

### Navegador Web

Simplemente visita: `http://localhost:5000`

La página principal muestra todos los endpoints disponibles con enlaces directos.

### cURL

```bash
# Petición simple (200 OK)
curl http://localhost:5000/success

# Endpoint protegido sin token (401 Unauthorized)
curl http://localhost:5000/protected

# Endpoint protegido con token válido (200 OK)
curl -H "Authorization: Bearer my-secret-token-12345" http://localhost:5000/protected

# Token inválido (401 Unauthorized)
curl -H "Authorization: Bearer token-incorrecto" http://localhost:5000/protected

# Bad Request (400)
curl http://localhost:5000/bad-request

# Forbidden (403)
curl http://localhost:5000/forbidden

# Not Found (404)
curl http://localhost:5000/notfound

# Created (201)
curl http://localhost:5000/created

# Conflict (409)
curl http://localhost:5000/conflict

# Rate Limited (429 después de 5 peticiones)
curl http://localhost:5000/rate-limited

# Internal Server Error (500)
curl http://localhost:5000/error

# Service Unavailable (503)
curl http://localhost:5000/service-unavailable

# Ver headers completos
curl -i http://localhost:5000/success

# Modo verbose
curl -v http://localhost:5000/success
```

### Python Requests

```python
import requests

# Petición simple
response = requests.get('http://localhost:5000/success')
print(f"Status: {response.status_code}")
print(f"Body: {response.text}")

# Con autenticación
headers = {'Authorization': 'Bearer my-secret-token-12345'}
response = requests.get('http://localhost:5000/protected', headers=headers)
print(f"Status: {response.status_code}")

# Verificar diferentes códigos
endpoints = ['/success', '/created', '/bad-request', '/error']
for endpoint in endpoints:
    r = requests.get(f'http://localhost:5000{endpoint}')
    print(f"{endpoint}: {r.status_code}")
```

### JavaScript/Fetch

```javascript
// Petición simple
fetch('http://localhost:5000/success')
  .then(response => {
    console.log('Status:', response.status);
    return response.text();
  })
  .then(data => console.log(data));

// Con autenticación
fetch('http://localhost:5000/protected', {
  headers: {
    'Authorization': 'Bearer my-secret-token-12345'
  }
})
  .then(response => response.text())
  .then(data => console.log(data));
```

### Bruno 

1. Descarga e instala Bruno desde su [sitio oficial](https://www.usebruno.com/)
2. crear petición GET
3. URL: `http://localhost:5000/protected`
4. En la pestaña **Authorization**:
   - Type: `Bearer Token`
   - Token: `my-secret-token-12345`
5. Envía la petición

## Testing Automatizado

### Script de prueba con bash

```bash
#!/bin/bash

BASE_URL="http://localhost:5000"
TOKEN="my-secret-token-12345"

echo "Testing HTTP Status Codes..."

# Test 200
curl -s -o /dev/null -w "GET /success: %{http_code}\n" $BASE_URL/success

# Test 201
curl -s -o /dev/null -w "GET /created: %{http_code}\n" $BASE_URL/created

# Test 401 (sin token)
curl -s -o /dev/null -w "GET /protected (no auth): %{http_code}\n" $BASE_URL/protected

# Test 200 (con token)
curl -s -o /dev/null -w "GET /protected (with auth): %{http_code}\n" \
  -H "Authorization: Bearer $TOKEN" $BASE_URL/protected

# Test 403
curl -s -o /dev/null -w "GET /forbidden: %{http_code}\n" $BASE_URL/forbidden

# Test 404
curl -s -o /dev/null -w "GET /notfound: %{http_code}\n" $BASE_URL/notfound

# Test 500
curl -s -o /dev/null -w "GET /error: %{http_code}\n" $BASE_URL/error
```

## Docker

### Comandos útiles

```bash
# Construir imagen
docker build -t http-status-code-server .

# Ejecutar en primer plano
docker run -p 5000:5000 http-status-code-server

# Ejecutar en segundo plano
docker run -d --name flask-server -p 5000:5000 http-status-code-server

# Ver logs
docker logs flask-server
docker logs -f flask-server  # Follow mode

# Entrar al contenedor
docker exec -it flask-server /bin/bash

# Detener contenedor
docker stop flask-server

# Reiniciar contenedor
docker restart flask-server

# Eliminar contenedor
docker rm -f flask-server

# Ver contenedores en ejecución
docker ps

# Ver todas las imágenes
docker images
```

### Puerto personalizado

```bash
# Mapear al puerto 8080 de tu máquina
docker run -d -p 8080:5000 http-status-code-server

# Acceder en: http://localhost:8080
```

## Troubleshooting

### El servidor no inicia

**Error:** `Address already in use`

**Solución:** El puerto 5000 está ocupado. Usa otro puerto:
```bash
docker run -p 8080:5000 http-status-code-server
```

### El token no funciona

**Verifica que estés usando el formato correcto:**
```bash
# Correcto
Authorization: Bearer my-secret-token-12345

# Incorrecto
Authorization: my-secret-token-12345
Authorization: Bearer: my-secret-token-12345
```

### No puedo acceder desde otra máquina

El servidor escucha en `0.0.0.0`, lo que permite conexiones externas. Verifica:
- Firewall de tu sistema
- Reglas de red de Docker
- Configuración de red de tu router

## Estructura del Proyecto

```
http-status-code/
├── server.py           # Código principal del servidor
├── Dockerfile          # Configuración de Docker
├── docker-compose.yaml # Configuración de Docker Compose (opcional)
└── README.md           # Este archivo
```

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Casos de Uso

Este servidor es útil para:

- 🧪 **Testing**: Probar cómo tu aplicación maneja diferentes códigos HTTP
- 📚 **Aprendizaje**: Entender los códigos de estado HTTP
- 🔧 **Desarrollo**: Mock server para desarrollo local
- 🤖 **CI/CD**: Testing automatizado de integraciones HTTP
- 📊 **Monitoring**: Probar sistemas de monitoreo y alertas

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## Autor

Creado como herramienta educativa y de testing para desarrollo web.

## Contacto

Para reportar problemas o sugerencias, por favor abre un issue en el repositorio.

---

**¡Disfruta probando códigos HTTP! 🚀**
