Basics
******

Despite it's size, this project only has one main app named huntserver which does nearly everything.
This page is meant to outline basic low level operational aspects and design choices of the server.
You can find more on how to effectively create and run a hunt in other pages.

Design
------
The design of this project is somewhat divided into two parts,
the staff experience and the hunter experience.

Staff is anyone that has the staff bit set in the admin page.
These users have access to the /staff/ area of the site;
however, in order to access all functions and access the /admin/ area of the site, the user must also be a superuser as designated by Django.

Dynamic Content
---------------
Dynamic content is created by using a combination of the model-view controller and the default Django templating engine.
Both are extensively documented on Django's website.
Both models and views used in this project are documented by later pages.

Static Content
--------------
Static files are managed by Django with each app having it's own collection of static files.
These files are gathered in the main static directory (``{PROJECT FOLDER}/static/`` )
by running ``python manage.py collectstatic``. 
This main static directory is not tracked by git,
and therefore you should not put any content directly into this folder. 

Puzzles should not be checked into the Github repository.
They should exist on some accessible online file source (we use Dropbox)
and will be downloaded and converted when the admin choses to do so.
Once downloaded, the puzzle files live in ``{PROJECT FOLDER}/media/puzzles/``
and are named using the "puzzle id" field of the puzzle which is enforced to be unique to each puzzle.

To protect users from being able to just go to ``/media/puzzles/{Puzzle_id}.pdf`` and get puzzles,
the server comes included with a protected routing path.
The /protected/ URL will only allow a user to access puzzle files if they have unlocked the puzzle.
To avoid hard-coding that path, you can use the variable "settings.PROTECTED_URL"  after importing the project settings.

It is a bit simplistic, but anything in the puzzles directory is permission guarded by the first 3 characters of the filename.
If the requesting user has access to the puzzle object with the corresponding 3 character puzzle_id, then they will have access to that file.
You can use this to protect files other than just the puzzle PDFs and PNGs.

You should protect your media URL by only allowing access to /media/ from internal sources.
The Apache configuration for this project includes protection like this already.

Database
--------
As noted in setup, the default database for this project is a MySQL database.
After setup the database should never need to be modified by hand,
additions or deletions should be done from the online admin GUI or if absolutely necessary, from the Django interactive shell.
Modifications to the table structure should only be done by modifying models.py
and using the automatically created migration files. 
