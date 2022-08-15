# AutoramosWeb
Plataforma web para tomar ramos automaticamente en banner PUC

# Instalación e iniciacion
1. Inicia un virtualenvirnoment
```
python3 -m venv venv
source venv/bin/activate
```

2. Instalar los requerimientos con:
```bash
pip install -r dev-requirements.txt
```

3. Crear un archivo .env y agregar las siguientes lineas:
```
#Django conf
export SECRET_KEY="ntf2w2#zuoo43m9a@j*r1529ab^-5_wdsea-$$+k()@ry#lxv8b"
export DEBUG=1
export HTTPS=0

#Postgres conf
export POSTGRES_TABLE_NAME=autoramosweb
export POSTGRES_USER=<usuario-postgres>
export POSTGRES_PASSWORD=<contraseña-postgres>
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432

#Mail conf (sendinblue)
export EMAIL_HOST=""
export EMAIL_PORT=""
export EMAIL_HOST_USER=""
export EMAIL_HOST_PASSWORD=""

#Celery conf
export CELERY_URL=amqp://localhost

#Selenium conf
export SELENIUM_REMOTE_URL='http://127.0.0.1:4444'
```

4. Agrega las variables de entorno a tu virtualenvironment
```bash
source .env
```

5. Iniciar celery 
```bash
#~/autoramosweb/
celery -A autoramosweb worker -l info 
celery -A autoramosweb beat
```

6. Crear archivo `docker-compose.yml`:
```yml
version: '3'

#Services
services:
  selenium:
    image: selenium/standalone-chrome
    environment:
      - SE_NODE_MAX_SESSIONS=5
      - SE_NODE_OVERRIDE_MAX_SESSIONS=true
    ports:
      - "4444:4444"
```

7. En el mismo directorio en donde se encuentra el `docker-compose.yml`, montar selenium standalone:
```bash
docker-compose build
docker-compose up -d
```
8. Montar el servidor Django
```
cd autoramosweb
python manage.py runserver
```