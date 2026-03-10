# vote-hub


VoteHub is a Django-based web application with a REST API where users can publish projects, vote for them, and leave comments. 
The API supports filtering, searching, ordering, and user authentication.


### Run project:


git clone https://github.com/zayacsk/vote-hub.git


cd vote-hub


python3 -m venv env


source env/bin/activate


python3 -m pip install --upgrade pip


pip install -r requirements.txt


create .env and add SECRET_KEY


cd vote-hub


python3 manage.py migrate


### Run server:


python3 manage.py runserver


### Get API documentation:


python3 manage.py runserver


http://127.0.0.1:8000/swagger/ or http://127.0.0.1:8000/redoc/
