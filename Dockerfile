# Utiliza la imagen base de Python
FROM python:3.9

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /proyecto-guayini

# Copia los archivos necesarios (asegúrate de incluir requirements.txt)
RUN mkdir -p  /proyecto-guayini/
COPY requirements.txt /proyecto-guayini/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia el contenido de tu aplicación en el contenedor
COPY GUAYINI/* /proyecto-guayini/GUAYINI/
COPY staticfiles/* /proyecto-guayini/staticfiles/
COPY tasks/* /proyecto-guayini/tasks/
COPY manage.py /proyecto-guayini/

# Configura variables de entorno para Django
 ENV DJANGO_SETTINGS_MODULE=GUAYINI.settings

# Ejecuta las migraciones de Django
RUN python manage.py migrate
# Establece la imagen base para Nlatestginx
FROM nginx:latest

# Copia la configuración de Nginx a la ubicación adecuada
COPY nginx.conf /etc/nginx/nginx.conf

# Copia los archivos estáticos de Django a la ubicación de Nginx
COPY --from=0 /app/static /static
