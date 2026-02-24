# a rewrite of philolog.us for react and django

To import data:  
python manage.py load_lexica   

To run development server:  
npm --prefix frontend run build && python manage.py runserver  

browse:  
http://localhost:8000/  

To build for production:  
docker build --load --builder multi-platform-builder --platform=linux/amd64,linux/arm64 -t philologus-react-django:tag .  

run:  
docker run -e ALLOWED_HOSTS="* localhost 127.0.0.1" -p 8080:80 philologus-react-django:tag  

browse:  
http://localhost:8080/
