# puzzlehunt_server
Server for Puzzlehunt CMU's bi-annual puzzlehunt. Includes basic features such as per-puzzle pages, automatic answer response, team logins, customizable unlocking structure, and admin pages to manange submissions, teams, as well as hunt progress. It also includes automatic team creation from registration, privacy settings for hunts, cool charts, a chat with the staff feature, and automatic file fetching and hosting. 

System packages:
* python 2.7
* mysql-client
* mysql-server
* python-mysqldb
* python-dev
* imagemagick
* libmysqlclient-dev

Python packages (pip)
* django
* MySQL-python
* python-dateutil

(Working on getting a virtualenv solution set up)

Database setup details:
* expects a pre-existing empty database named puzzlehunt_db
* Database settings are in puzzlehunt_server/secret_settings.py the example used below has the following settings:
 a user named ```hunt``` on domain ```localhost``` with password ```wrongbaa``` with access to ```puzzlehunt_db```. Production values should be different. 
* The above can be accomplished by running the following commands as a superuser:
   * ```CREATE DATABASE puzzlehunt_db;```
   * ```CREATE USER 'hunt'@'localhost' IDENTIFIED BY 'wrongbaa';```
   * ```GRANT ALL PRIVILEGES ON puzzlehunt_db.* TO 'hunt'@'localhost' WITH GRANT OPTION;```
* run ```python manage.py migrate``` to have django configure the database
* then run ```python manage.py runserver 8080``` to start a server at http://127.0.0.1:8080/ (this will be replaced with nginx in the production version)
 

Project Details:
* Check out file_map.txt for new developers.
* The django project is named ```puzzlehunt_server``` amd the app is named ```huntserver```
* Instructions to start the server can be found in notes.txt

Desired Features
- [ ] Ability to set interactive unlocks and give notifications
- [ ] Hints
- [ ] Public facing charts and leaderboard (disableable)
