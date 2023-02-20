## philolog.us for django

To install:  

Install Solr  
create Solr core with default configuration  

/path/to/solr/bin/solr create -c mycollection -s 2 -rf 2  

create a python virtual environment  

pip install -r requirements.txt  

To use with postgresql:  

CREATE DATABASE philolog_django WITH ENCODING 'UTF-8' LC_COLLATE='en_US.UTF-8' TEMPLATE template0;  
ALTER ROLE <rolename> SET client_encoding = 'UTF-8';  

set environment variables for db connection. use .env file.  

python manage.py makemigrations  
python manage.py migrate  

For postgresql, change columns to use Greek unicode collation:  

ALTER TABLE philolog_word ALTER COLUMN word SET DATA TYPE character varying(255) COLLATE "el-x-icu";  
ALTER TABLE philolog_word ALTER COLUMN definition SET DATA TYPE text COLLATE "el-x-icu";  

Import data from respective git repos into Solr and Django:  

python manage.py load_lexica  

python manage.py runserver  
