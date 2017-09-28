# puzzlehunt_server
Server for Puzzlehunt CMU's bi-annual puzzlehunt. Includes basic features such as per-puzzle pages, automatic answer response, teams, customizable unlocking structure, and admin pages to manange submissions, teams, as well as hunt progress. It also includes automatic team creation from registration, privacy settings for hunts, cool charts, a built in chat, and automatic file fetching and hosting. 
	
System packages:
* python 2.7
* mysql-client
* mysql-server
* python-mysqldb
* python-dev
* libmysqlclient-dev

See requirements.txt for Python requirements

Database setup details:
* expects a pre-existing empty database named puzzlehunt_db
* Database settings are in puzzlehunt_server/secret_settings.py the example used below has the following settings:
 a user named ```hunt``` on domain ```localhost``` with password ```wrongbaa``` with access to ```puzzlehunt_db```. Production values should be different. 
* The above can be accomplished by running the following commands as a superuser:
   * ```CREATE DATABASE puzzlehunt_db;```
   * ```CREATE USER 'hunt'@'localhost' IDENTIFIED BY 'wrongbaa';```
   * ```GRANT ALL PRIVILEGES ON puzzlehunt_db.* TO 'hunt'@'localhost' WITH GRANT OPTION;```
* run ```python manage.py migrate``` to have django configure the database 

Project Details:
* The django project is named ```puzzlehunt_server``` amd the app is named ```huntserver```
* Documentation (a work in progress) can be found at docs.puzzlehunt.club

While there is fairly large amount of configuration making this specific to Puzzlehunt CMU, if you are interested in getting this running elsewhere, let me know. I'd be happy to help anyone who wants to get this up and running for their needs. 
	
Please submit issues for any bugs reports or feature requests.
