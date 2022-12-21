# stail - API for Saturnalia'22


Users have to Sign Up for the website, and then they can verify their email id using the link sent on their registered id. Users can log in and register for multiple events/competitions after email verification and can create a team and share the team code with other team members to join their team. Non-Thapar users will receive an email for the payment of the requisite fees for participation in the event. Post payment verification, their registration will get confirmed. All emails are stored in the database and sent later at intervals using multiple email ids. Memcached is used to reduce repetitive database calls and improve performance.






## Tech Stack

**Client:** HTML, CSS, Bootstrap

**Server:** Python, Django, Django REST framework

**Database:** PostgreSQL

**Cache:** Memcached


  
## Run Locally


Clone the project

```bash
  git clone https://github.com/askandola/stail.git
```

Go to the project directory

```bash
  cd stail
```

We recommend you to use virtual environment

```bash
  python -m venv venv
```

Activate virtual environment   
For Windows PowerShell
```bash
    venv/Scripts/activate.ps1
```
For Linux and MacOS
```bash
    source venv/bin/activate
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Make sure you have installed PostgreSQL and Memcached

Create *.env file* and place Security-Key and Database credentials.

Run Migrations

```
 python manage.py makemigrations
```
```
 python manage.py migrate
```

Start the server

```bash
  python manage.py runserver
```



  
## Team

* [Chandravo Bhattacharya](https://github.com/Chandravo)
* [Arvinder Singh Kandola](https://github.com/askandola)
