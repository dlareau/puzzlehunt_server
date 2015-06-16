# puzzlehunt_server
Server for Puzzlehunt CMU's bi-annual puzzlehunt.

Setup details:
* requires mySQL, python 2.7 and django
* expects a pre-existing database named puzzlehunt_db
* expects a user named ```hunt``` on domain ```localhost``` with password ```wrongbaa``` with access to ```puzzlehunt_db```
* The above can be accomplished by running the following commands as a superuser:
   * ```CREATE DATABASE puzzlehunt_db;```
   * ```CREATE USER 'hunt'@'localhost' IDENITFIED BY 'wrongbaa';```
   * ```GRANT ALL PRIVILEGES ON puzzlehunt_db.* TO 'hunt'@'localhost' WITH GRANT OPTION;```
* run ```python manage.py migrate``` to have django configure the database
* then run ```python manage.py runserver 8080``` to start a server at http://127.0.0.1:8080/ (this will be replaced with apache in the production version)
 

Project Details:
* Planned models and views can be found and contributed to [here](https://docs.google.com/document/d/1m_et2SfdcPdOuWgtSCfs9RXN9QTxW9WGgjHZsOQ2yFo/edit)
* The django project is named ```puzzlehunt_server``` amd the app is named ```huntserver```
* We are using setup and coding practices taken from the django tutorial [here](https://docs.djangoproject.com/en/1.8/intro/tutorial01/)
* There is a branch with the tutorial server mentioned above up to halfway through the 4th part for code refrence.


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
