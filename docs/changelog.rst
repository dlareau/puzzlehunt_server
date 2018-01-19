*********
Changelog
*********

Version 3
*********

v3.1.0
======

New:
   -  Users can now update their profile information including name, email, phone, and food preferences
   -  Teams can now update their own location from the registration page
   -  Automatic submission responses now support markdown style links
   -  Progress page now has a button to unlock a specific puzzle for all teams

Updates:
   -  Removed unlockables tab from hunt header due to disuse
   -  Progress and Queue page now have sleeker more compact look
   -  Hunt info page now pulls max team size from database
   -  "Contact us" page now has more contact info

Bugfixes:
   -  Fixed bug where team names could be made entirely of whitespace characters
   -  Removed dummy teams from all normal hunt interactions
   -  Fixed bug where parts of old hunt headers lead to the current hunt pages
   -  Fixed bug where staff announcements triggered new message alert for other staff members.

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