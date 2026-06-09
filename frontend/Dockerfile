# Usamos una imagen oficial y ligera de Nginx basada en Alpine Linux
FROM nginx:alpine

# Copiamos nuestro archivo index.html dentro del directorio público por defecto de Nginx
COPY index.html /usr/share/nginx/html/

# Exponemos el puerto 80 que es el que usa Nginx por defecto
EXPOSE 80

# Nginx se ejecuta automáticamente, no hace falta declarar un CMD complejo