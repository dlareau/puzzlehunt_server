# puzzlehunt_server
Server originally for Puzzlehunt CMU's bi-annual puzzlehunt. Includes basic features such as per-puzzle pages, automatic answer response, teams, customizable unlocking structure, and admin pages to manange submissions, teams, as well as hunt progress. It also includes automatic team creation from registration, privacy settings for hunts, cool charts, a built in chat, and automatic file fetching and hosting. 

This branch is dedicated to having a generic version of the server that anybody can use for their own puzzlehunt. It removes all mentions of CMU, and CMU specific implementation details. 

Documentation can be found at http://docs.puzzlehunt.club, though it still is slightly CMU specific. 

To get this version set up for your own uses, edit the specified spots in the "contact_us", "hunt_info" and "index" templates, designated by 4 hash marks ("####"). 

This version also includes an easy install script to make installation easier. Simply download the script ("easy_setup.sh") from github, place it on a newly set up Debian or Ubuntu server and run it with root privalages. It will take care of installing all prerequisite packages and configuring the server for basic usage. 
	
Please submit issues for any bugs reports or feature requests.
