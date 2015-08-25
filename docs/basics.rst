Basics
******

This project is pretty basic as far as Django projects go,
it has one main app named huntserver which does nearly everything.
Consult file_map.txt for a basic layout of the project.

Design
------
The design of this project is somewhat divided into two parts,
the staff experience and the hunter experience.
Staff is considered to be anyone logged in using an account with a username in the ADMIN_ACCTS setting.
(found in secret_settings)
These users have access to the /staff/ area of the site;
however, in order to access all functions and access the /admin/ area of the site,
the user must also be a superuser as designated by Django. 

Dynamic Content
---------------
Dynamic content is created by using a combination of the model-view controller and the default Django templating engine.
Both are extensively documented on Django's website.
Both models and views used in this project are documented by later pages.

Static Content
------------
Static files are managed by Django with each app having it's own collection of static files.
These files are gathered in the main static directory (``{PROJECT FOLDER}/static/`` )
by running ``python manage.py collectstatic``. 
This main static directory is not tracked by git,
and therefore you should not put any content directly into this folder. 

Puzzles should not be checked into the Github repository.
They should exist on some accessible online file source (we use Dropbox)
and will be downloaded and converted when the admin choses to do so.
Once downloaded, the puzzle files live in ``{PROJECT FOLDER}/huntserver/static/huntserver/puzzles/``
named using the puzzle ids that are unique. 

To protect users from being able to just go to ``/static/{Puzzle_id}.pdf`` and get puzzles,
the server comes included with a protected routing path.
The /protected/ URL will only allow a user to access puzzle files if they have unlocked the puzzle.
This routing path will automatically be used as long as access to static files
is done through the template command ``{STATIC_URL}``.
You should protect your static URL by only allowing access to /static/ from internal sources as 
described in the "Setup: Nginx" portion of these docs. 

Websockets
----------
This project accomplishes live page content with the use of websockets powered by ws4redis.
These websockets are controlled by a redis message passing server running alongside the django server.
This allows asynchronous communication to the clients webpage,
however communication from the webpage is synchronous with respect to the Django server.
This limitation is overcome by using POST requests as an asynchronous method of communication with the server from the client. 

Database
--------
As noted in setup, the default database for this project is a MySQL database.
After setup the database should never need to be modified by hand,
additions or deletions should be done from the Django interactive shell or from the online admin GUI.
Modifications to the table structure should only be done by modifying models.py
and using the automatically created migration files. 
