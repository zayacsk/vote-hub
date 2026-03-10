# vote-hub


VoteHub — a Django app with authentication, project CRUD, voting system, and comments.


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


python3 manage.py runserver


### Get API documentation:


http://127.0.0.1:8000/swagger/ or http://127.0.0.1:8000/redoc/
