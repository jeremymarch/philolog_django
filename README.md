# A Rewrite of philolog.us using react and django

## Installation  
git clone https://github.com/jeremymarch/philolog_django.git  
cd philolog_django  
python3 -m venv .venv  
source .venv/bin/activate  
pip install -r requirements.txt  
npm --prefix frontend install  
python manage.py migrate  

## To import data:  
python manage.py load_lexica   

## To run development server:  
npm --prefix frontend run build && ALLOWED_HOSTS="localhost" DJANGO_SECRET_KEY="ABC" python manage.py runserver  

browse:  
http://localhost:8000/  

## To build for production:  
npm --prefix frontend run build && docker build --load --builder multi-platform-builder --platform=linux/amd64,linux/arm64 -t philologus-react-django:tag .  

run locally (replace host on production):  
docker run -e ALLOWED_HOSTS="localhost 127.0.0.1" -p 8000:80 philologus-react-django:tag  

browse:  
http://localhost:8000/
