###### **Mini Wallet Exercise**

Wallet Service implemented with Python/ Django/ REST.
It exposes API's for :

###### **Get Wallet Balance**

Deposit to wallet

Withdraw from wallet

Get wallet Mini-statement.

List all registered accounts. (Admin)

List all transaction history (Paginated) (Future Use).

For now, creation of wallet is handled through admin.

**Requirements:**
Python==3.8.9

asgiref==3.4.1

backports.zoneinfo==0.2.1

Django==4.0.1

django-environ==0.8.1

djangorestframework==3.13.1

psycopg2-binary==2.9.3

pytz==2021.3

sqlparse==0.4.2


Uses Postgresql database. Can be extended easily to use any database.

Steps to run server:
**pip install -r requirements.txt

python manage.py migrate

python manage.py runserver

Server would be available at http://127.0.0.1:8000/**
