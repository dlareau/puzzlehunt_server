# puzzlehunt_server
Server for Puzzlehunt CMU's bi-annual puzzlehunt.

Setup details:
* requires mySQL, python 2.7 and django
* expects a pre-existing database named puzzlehunt_db
* run ```python manage.py migrate``` to have django configure the database
* then run ```python manage.py runserver 8080``` to start a server at http://127.0.0.1:8080/ (this will be replaced with apache in the production version)


Base Features:
* Answer Submission
* Team ID sign in and view stats
* Answer response system
* Landing Page
* admin view (Same as now)
* Graph unlocking structure


Desired Features
* Charts 
* Hints
* Manual response being correct
* Admins be able to see manual responses
* Send more than one manual response
* Multiple Landing pages
* Show top k teams without score
* Solve count for each puzzle publice
* Very clear puzzle labeling
* Ability for puzzle solutions to unlock objects
* Server can get puzzles from links using button on admin page.
