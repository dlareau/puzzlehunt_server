*********
Changelog
*********

Version 4
*********

v4.1.0
======
New: 
   - Added in-page HTML puzzles
   - Added lookup staff page
   - Added autocomplete fields to admin
   - Add github CI
   - Moved to file uploads from URLS/downloads.

Updates:
   - Chat now has 2 min polling on all hunt pages
   - Better chat notifications
   - Redirect to login screen more often when permissions are wrong
   - Removed individual unlock buttons from progress page
   - Shibboleth works on traefik reverse proxy now
   - Navbar rewrite
   - Locust updates
   - Deployment tweaks

Bugfixes:
   - Don't ratelimit by team for past hunts
   - Removed hint submission box when hunt is public
   - Display end date for multi-day hunts
   - Fix flatpages deployment bugs
   - More hint bugfixes


v4.0.0
======

New:
   - Now requires Django 2.2 (and therefore requires Python 3)
   - Added hints

      - Staff can now set various rules for when to grant teams hint requests
      - Once a team has a hint request, they can request a hint for a specific puzzle
      - There are new pages for requesting, viewing, and answering hints
   - Added the ability to unlock puzzles using points (time)

      - Puzzles can now be unlocked through solves or points
      - Points can be gotten by solving puzzles and/or over time (both settable via the admin interface)
   - Information pages are now editable via the admin interface

      - All "information pages" except for the homepage are now editable via the "info pages" admin section
      - It is possible to add additional extra pages to the top navbar via the admin interface
   - The download command output is now displayed when downloading puzzles and resources
   - All of the main python files in the project are now PEP8/flake8 compliant
   - Standard deployment is now all done through docker and docker compose
   - Very large documentation update. Now has actually helpful docs for hunt creation and running

Updates:
   - Puzzle PDFs are now directly embedded in puzzle pages rather than using PNGs
   - The progress page now sorts by last overall time rather than meta/non-meta time individually
   - Almost all forms on both user and staff pages are now styled using bootstrap
   - Many admin pages now support better searching, filtering and sorting of items
   - Puzzle ID's can now be up to 5 hexadecimal digits (up from 3)
   - Teams can now register in the 2 days before the hunt but cannot request a room
   - Updated text on index and hunt info pages to work for multi-day hunts
   - Due to points/time puzzles, playtest teams now must have a start and end date/time
   - The submission box now goes away after a team submits a correct answer
   - Removed the "submissions after solve" chart on the admin "Charts" page
   - Removed the hidden "depgraph" staff page
   - Tweaked ratelimits, they are now more restrictive
   - The test suite no longer requires internet access to run
   - Removed reliance on django-nose, six, and PyPDF libraries

Bugfixes:
   - Informational logs no longer cause an error when presented with a unicode character
   - Media path bug fixed
   - Fixed logout redirect when shibboleth is disabled
   - Various typo, readability, and small bug fixes

Version 3
*********

v3.5.0
======

New:
   - Teams can now no longer change their name within 2 days of the hunt
   - It is now possible to easily assign rooms to many teams from the info page
   - Added basic informational logging to the huntserver app

Updates:
   - Nicer pages and messages displayed when a user doesn't have access to an area
   - Many code changes made to allow easier deployment of a generic version
   - Single puzzle unlock now has a confirmation popup
   - Added some look/feel features to staff chat to improve clarity
   - Ratelimits have been stacked and tightened down to a more reasonable level
   - Server now supports 5 digit puzzle IDs

Bugfixes:
   - Fixed ability to log into dev server using shibboleth
   - Fixed bug that meant solutions could only be downloaded for the current hunt

v3.4.0
======

New:
   - Puzzles and hunts now have an additional field for generic data storage
   - Puzzle solution PDFs can now be entered and displayed after the hunt ends
   - Queue can now be filtered by team and/or puzzle
   - Hunts can now have a "resources" link for additional static content
   - Chat link in navbar now has a "number of unread messages" badge
   - Ctrl/Cmd-S now will now save the current mode in the django admin

Updates:
   - The announcement checkbox in staff chat now automatically get unchecked after sending
   - The "Current Hunt" link now has time sensitive behavior for before/during hunts
   - Due to the addition of hunt resources, hunt asset files are now deprecated
   - Updated wording to Previous/Current/Next hunt on the index page based on date
   - The hunt management page has been redesigned for easier usage
   - Most staff pages now have been updated to better utilize bootstrap

Bugfixes:
   - Fixed progress page bug which update initial solve time if solved again
   - Fixed sorting bug on the progress page regarding meta-solve-time
   - Fixed a bug where the queue would roll items to the next page when not needed
   - Fixed a number of small CSS errors and typos

v3.3.0
======

New:
   - Python 3 compatibility
   - Now requires Django 1.11 (Start of Django 2.0 compatibility)
   - New testing and coverage framework, including integration with travis-ci/coveralls
   - New admin layout that supports new Django version
   - Added "Info" page for staff showing team locations and allergies
   - New load testing framework
   - Added support for "HTML puzzles" that are just a webpage rather than a PDF
   - Added support for customizable prepuzzles.

Updates:
   - Setup script is now idempotent
   - Added information to previous hunt page
   - Many minor fixes to reduce server load
   - Hunt start and end dates are now controllable independently from display dates
   - Progress page now sortable by success metrics

Bugfixes:
   - First message no longer gets lost when sent by staff
   - Teams now automatically get deleted if all users leave before the hunt starts
   - Past hunts now viewable when not logged in

v3.2.0
======

New:
   - Common punctuation ( _-;:+,.!?) is now automatically stripped from puzzle answer submissions
   - All string fields now support unicode characters
   - Puzzle answer submissions are now ratelimited to 10 submissions per minute
   - New charts and other info on charts page
   - Puzzle pages now show a solve count
   - Teams can now update their name before the hunt starts from the team management page

Updates:
   - Staff chat now allows staff to initiate conversations with teams
   - Chat now automatically scrolls to the bottom upon loading and new messages
   - Minor style changes including navbar and team name rendering

v3.1.1
======

Updates:
   - Updated documentation to include instructions for hunt asset files

v3.1.0
======

New:
   -  Users can now update their profile information including name, email, phone, and food preferences
   -  Teams can now update their own location from the registration page
   -  Automatic submission responses now support markdown style links
   -  Progress page now has a button to unlock a specific puzzle for all teams
   -  New 404 and 500 error pages to match website's style

Updates:
   -  Removed unlockables tab from hunt header due to disuse
   -  Progress and Queue page now have sleeker more compact look
   -  Hunt info page now pulls max team size from database
   -  "Contact us" page now has more contact info
   -  Unused /staff URLs will now route to /admin URLs

Bugfixes:
   -  Fixed bug where team names could be made entirely of whitespace characters
   -  Removed dummy teams from all normal hunt interactions
   -  Fixed bug where parts of old hunt headers lead to the current hunt pages
   -  Fixed bug where staff announcements triggered new message alert for other staff members.
   -  Fixed bug in 3.0.3 relating to the use of "is not None" in info_views

v3.0.3
======

New:
   -  Documentation of models, views, configuration, and how to run the server.

v3.0.2
======

Bugfixes:
   -  Fixed bug where chat would throw an error if the hunt did not have any messages yet
   -  Fixed bug where sometimes staff chat button remapping script wouldn't load

v3.0.1
======

Bugfixes:
   -  Fixed bug where staff had to have puzzle unlocked to view puzzle

v3.0.0
======

New:
   -  Staff interaction with server via SSH is no longer necessary for normal hunt creation

      -  The template for each puzzlehunt is now editable from an web-based inline editor

         -  The editor is located on the admin page for each hunt
         -  The editor supports syntax highlighting for HTML and CSS
         -  **HTML files in the template folder of the form hunt#.html are now useless**

      -  Hunt-specific web assets such as fonts and images can now be uploaded from admin interface

         -  Assets are stored in the /media/hunt/assets/ directory

      -  Hunt specific files should no longer be included in the repository


.. only:: latex

   Older Versions
   **************

   You can find the changelog for older versions in the online documentation
   at https://docs.puzzlehunt.club

.. only:: html

   Version 2
   *********

   v2.7.2
   ======

   Updates:
      -  Added password reset link to login page

   v2.7.1
   ======

   Bugfixes:
      -  Fixed issue with custom tabular template that prevented editing puzzle details
      -  Various typo fixes on the login selection page

   v2.7.0
   ======

   New:
      -  Progress page now shows last submission time for unsolved team/puzzle squares
      -  Staff chat now supports announcements to all teams
      -  Added 3 new charts to the staff charts page

   v2.6.4
   ======

   Bugfixes:
      -  Fixed bug where previous hunt page would also show future hunts

   v2.6.3
   ======

   Updates:
      -  Offsite and dummy teams are no longer shown in charts

   v2.6.2
   ======

   Bugfixes:
      -  Fixed bug where looking at an open hunt while not on a team would cause an error

   v2.6.1
   ======

   Updates:
      -  Changed staff header contents to be relevant to website content

   v2.6.0
   ======

   New:
      -  Added simplistic rendering of unlocking structure graph
      -  Added ability to reset password via email for local accounts
      -  Added ability to send email to all hunt participants directly from the email page
      -  Added ability to update local PDF of individual puzzles
      -  Added ability to edit puzzle responses from the respective puzzle page

   Updates:
      -  **Puzzle unlocking GUI has been reversed, now selects which puzzles unlock current puzzle**
      -  Regex for responding to answers is now case-insensitive
      -  New CSS style for staff pages using updated bootstrap theme
      -  Default action for incorrect responses is now the "Canned Response" instead of nothing

   Bugfixes:
      -  Current hunt link no longer changes destination depending on current page
      -  Patched several security vulnerabilities related to account registration and Shibboleth

   v2.5.2
   ======

   Bugfixes:
      -  Removed bad staff footer
      -  Fixed incorrect contact information

   v2.5.1
   ======

   Updates:
      -  Updated "Not Released" page style to match the rest of the pages

   Bugfixes:
      -  Fixed bug where correct answers on old hunts were styled as wrong answers
      -  Fixed bug where puzzle page would "lose" a submission response

   v2.5.0
   ======

   New:
      -  All pages now support google analytics tracking

   v2.4.1
   ======

   Bugfixes:
      -  Fixed URL for University of Pittsburgh IDP

   v2.4.0
   ======

   New:
      -  Staff queue now is paginated for faster load times
      -  Submissions may now be computationally responded to using regexes
      -  Old hunts are now preserved properly and playable
      -  Server now supports "Playtesting" teams who get early access to puzzles
      -  AJAX requests now only fire when the page is active to reduce web traffic
      -  Correct answer submissions may now have response texts other than "Correct!"
      -  Support for running simultaneous development server(s)

         -  Identifying header when on development server
         -  Django debug toolbar present when on development server

   Updates:
      -  Setting the current hunt is now done on the control page instead of the settings file
      -  Updated look of staff chat, switched to side tabs for usability
      -  Server now uses PyPDF2 to get PDF length to lessen reliance on outside tools
      -  AJAX code updated to support model based data generation
      -  Moved all in-page javascript to separate files
      -  Removed all Redis websocket code from codebase
      -  All effectful web requests are now done in POST requests

   Bugfixes:
      -  Fixed bug where staff members had to be on a team for the queue to update
      -  Fixed bug where local clock skew would cause the queue to miss updates
      -  Fixed bug where AJAX would fail if there weren't any submissions yet
      -  Shibboleth will now default to local login when not configured
      -  Removed unnessecary CSRF token from certain GET requests

   v2.3.0
   ======

   New:
      -  Moved from websocket/subscription model to AJAX/polling model for efficiency and simplicity

   v2.2.0
   ======

   New:
      -  Resources page now contains helpful links
      -  Users are now able to leave a team from the registration page
      -  Users are now able to see their room assignment from the registration page

   Updates:
      -  Configuration files are now in a separate directory
      -  Apache is now configured to use uWSGI emperor mode
      -  Improved registration page
      -  Static files are now served using Apache and X-Sendfile for efficiency

   Bugfixes:
      -  Username is now hidden when the navbar is too small to display it properly
      -  Various bug fixes related to properly creating Shibboleth accounts

   v2.1.0
   ======

   New:
      -  Server now supports Shibboleth authentication for users

   v2.0.1
   ======

   Bugfixes:
      -  Fixed improper unicode method on Person object
      -  Visiting a hunt's page while not on a team no longer results in an error

   v2.0.0
   ======

   New:
      -  Server now is one account per person instead of one account per team

         -  Registration is completely re-written
         -  Websocket code for most pages is re-written (relied on user)
         -  Old databases are incompatible and must be regenerated

            -  Migration files restarted at 0001
            -  No automatic way to migrate data from previous scheme

      -  Added new informational pages

         -  New home page with organization details!
         -  Other information pages such as "Contact Us" and "Resources"

   Updates:
      -  ADMIN_ACCTS variable no longer used anywhere and removed
      -  Page load time improvements to Progress and Queue staff pages


   Version 1
   *********

   v1.3.0
   ======

   Updates:
      -  All pages now styled with bootstrap
      -  All staff/admin views now rely on the "Staff" label instead of ADMIN_ACCTS

   v1.1.1
   ======

   Bugfixes:
      -  Re-fixed bug where users are able to submit answer when hunt is not open
      -  Fixed XSS vulnerability in chat updating
      -  Fixed broken link to goat.mp3
      -  Fixed unnecessary response of full HTML page for ajax requests.

   v1.1.0
   ======

   New:
      -  Added text to registration page to assist in registration
      -  Added Emails page for easy access to hunter's emails
      -  Location is now a field when registering
      -  Users are now able to view an existing registration with password

   Updates:
      -  Static files are now collected after downloading puzzles

   v1.0.1
   ======

   Bugfixes:
      -  Fixed issue with chat websockets not sending properly

   v1.0.0
   ======

   New:
      -  Added documentation!

   Updates:
      -  Phone number is no longer a required field in registration
      -  Puzzles are now automatically unlocked for newly registered teams


   Pre-release
   ***********

   v0.6.0
   ======

   New:
      -  Teams may now have a size limit
      -  Static file access is now protected by unlock structure

   Updates:
      -  Answer box now clears upon submission
      -  Puzzle image quality improved
      -  Code is better commented
      -  Important private settings have been moved to an untracked file
      -  PDFs are now served from the local downloaded copy

   Bugfixes:
      -  Puzzles may no longer be solved when the hunt is not open

   v0.5.0
   ======

   New:
      -  Added Hunt Control page with actions to reset or release all puzzles
      -  Added chat functionality to allow hunters to chat with staff
      -  Added images of puzzles on each puzzle page
      -  Added ability to unlock objects upon a puzzle solve
      -  Added Unlockables page to view unlocked objects
      -  Added Registration page to allow self registration of teams

   Updates:
      -  Responses are now changeable after submitting

   Bugfixes:
      -  Progress page no longer displays UTC times
      -  Fixed XSS vulnerability in Queue page
      -  Users can now only be on 1 team

   v0.4.0
   ======

   New:
      -  Added "Access Denied" page and appropriate logic
      -  Added "Staleness coloring" on progress page
      -  Added Team/Puzzle status chart to charts page

   Updates:
      -  Puzzle ID's are now unique
      -  Phone number no longer required for Team creation
      -  Updated style of header

   v0.3.0
   ======

   New:
      -  Added Progress page to show all teams' progress
      -  Added support for live updating on Progress page

   Updates:
      -  Styled built-in admin pages to look like staff pages

   v0.2.0
   ======

   New:
      -  Added Login, Landing, Puzzle and Queue pages
      -  Added answer submission on puzzle page and answer viewing on queue page
      -  Added websocket functionality to allow Puzzle and Queue pages to update live

   v0.1.0
   ======

   New:
      -  Django webserver with base models and views
      -  Deployment configuration for nginx and mySQL
