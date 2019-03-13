How to Create a Hunt
********************

Below are all of the steps you should need to take to create a puzzlehunt and have it ready to run:

Create Hunt Object
==================

You aren't going to get very far without a hunt object to attach all of this data to, so sign in with a staff account and navigate over to ``{server URL}/admin/huntserver/hunt/``

Click the "+" button at the top. 

You will be brought to the hunt creation page, which you should fill out, keeping in mind the following points:

  - Make sure the start date is accuratej or at the very least in the future, otherwise people will be able to see your hunt immediately.
  - Make sure the end date is **after** the start date.
  - Do not check the "Is current hunt" box just yet
  - See the section below before putting anything into the template editor.

Just to be safe, go ahead and click the "Save and continue editing" before moving onto the next section.

Edit Hunt Template
==================

Basic information
-----------------
This is where we give the hunt it's look and feel. Before this point, navigating to /hunt/{hunt_number} would just give you a blank page. 

Everything typed into the "Template" form on the hunt editing page will be run through django's templating engine and rendered as HTML. 

The following context will be passed to the renderer for use in the template: ``{'hunt': ... , 'puzzles': ... , 'team': ... , 'solved': ...}`` where 'hunt' is the current hunt object, 'puzzles' is the list of puzzle objects that the team has currently unlocked, 'team' is the team of the user that is viewing the page, and 'solved' is the list of puzzle objects that the team has currently solved. All of those are pretty self explanatory.

**While you may use completely custom HTML, it is STRONGLY RECOMMENDED that you follow the instructions below on how to inherit the base template to get nice features like the header bar, common style sheets, google analytics, and graceful degradation when the hunt becomes public.**

A note about static files
-------------------------

As of version 3.0.0, in order to reduce repository clutter, it is now against policy to commit files specific to a certain hunt to the respository. This means that you are no longer allowed to put images, fonts, and other files in ``/huntserver/static`` or ``/static``. 

As of version 3.4.0, the "hunt asset" system has been deprecated in favor of the new "hunt resources" system.

To still allow the use of new static files in each hunt, there is now a field on each hunt's admin page for a resource URL. This URL should point to a publicly accessible zip file, which contains all static media needed for the main hunt page. The resources can be downloaded by clicking the "Resources" button next to the appropriate hunt on the Hunt Management page.

After the resources have been downloaded, they will be accessible through the use of a special template tag: ``{% hunt static %}myimage.png``.


Inheriting the base template
----------------------------

If you don't already know about how Django template inheritance and blocks work, you can go read up on them here: https://docs.djangoproject.com/en/1.8/ref/templates/language/#template-inheritance 

I promise it won't take too much time to read, isn't too hard to understand, and will make the content below understandable.

Now that you know about blocks and inheritance, You'll want to start with the following template code at a minimum:

.. code-block:: html

  {% extends "hunt_base.html" %}

  {% block content %}
    Your content here
  {% endblock content %}

That is the most basic example you can get and will look very bland. Here are some other blocks you can override to get additional custom behavior:

title
  Overriding the 'title' block with whatever content you want to show up in the tab title. The default value for this block is "Puzzlehunt!"

base_includes
  Overriding the 'base_includes' block will insert content before the standard bootstrap and jquery imports allowing you to override unwanted boostrap styles. The default value for this block only imports hunt_base.css.

includes
  Overriding the 'includes' block will insert content after the standard bootstrap and jquery imports, for content that you want to use to extend those libraries, or content that relies on those libraries.

footer
  Overriding the 'footer' block will insert content at the bottom of the page. The default value is links to our social media and bridge page. 

Starter example
---------------

While you may have all of the information you need, that doesn't mean you know what to do with it. Below is a simple example based on our first hunt. It will show the puzzles, display the answer for any solved puzzles, and demonstrates how to insert a break a hunt into two rounds.

.. code-block:: html

  {% extends "hunt_base.html" %}
  {% block title %}Puzzles!{% endblock title %}
  
  {% block base_includes %}
  <link rel="stylesheet" type="text/css" href="{{ STATIC_URL }}huntserver/hunt_base.css">
  <style>
  .puzzle-name {
    white-space: nowrap;
    overflow: hidden;
    width: 320px;
  }
  </style>
  {% endblock base_includes %}
  
  {% block content %}
  <div class="container" >
    <div class="row" >
      <div class="content col-md-6 col-md-offset-3" id='puzzle-frame'>
        <h1 class="title">Puzzlehunt: The Musical</h1>
        <div id="puzzles">
          <table>
            <thead>
              <tr>
                <th style='width: 320px'>Puzzle Name</th>
                <th style='width: 180px'>Solution?</th>
              </tr>
            </thead>
            <tbody>
              {% for puzzle in puzzles %}
                {% if puzzle.puzzle_number == 8 %}
                  </tbody>
                  </table>
                  <h3 class="title">- Intermission -</h3>
                  <table>
                    <tbody>
                    <col width="320px">
                    <col width="180px">
                {% endif %}
                <tr id='puzzle{{ puzzle.puzzle_number }}' class='puzzle'>
                  <td>
                    <p class="puzzle-name">
                      <a href='/puzzle/{{ puzzle.puzzle_id }}/'>
                        {{puzzle.puzzle_name}}
                      </a>
                    </p>
                  </td>
                  <td>
                    {% if puzzle in solved %}
                      {{ puzzle.answer|upper }}
                    {% endif %}
                  </td>
                </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
        <p> Feeling stuck? <a href="/chat/">Chat</a> with us</p>
      </div>
    </div>
  </div>
  {% endblock content %}

Create Puzzle Objects
=====================

Great, now we have a hunt template and we can view our hunt, but that's not good without any puzzles, so lets add some. 

Start by going to ``{server URL}/admin/huntserver/puzzle/`` and clicking the "+" button at the top. 

You will be brought to the puzzle creation page, which you should fill out, keeping in mind the following points:

  - Puzzle number should ideally be incremental starting at 1, this will be used for ordering puzzles
  - Puzzle ID should be unique across all puzzles ever made, and it is good practice to have the last two digits match the puzzle number
  - Make sure to check the "Is meta" box if this puzzle is a metapuzzle. 
  - You don't need to fill in num pages, the server will do that for you upon downloading the pdf
  - Num required to unlock represents the number of puzzles in the below list that need to be solved to unlock this puzzle. Any puzzle with a '0' here will be considered part of the initial set
  - Don't worry about "Responses" right now, we'll talk about that below.
  - There are 3 link fields, all should be publicly accessible (no auth require) and include the full "https://":
  
    - "Link" should be a link to the PDF of the puzzle if this is not an HTML puzzle.
    - "Resource Link" should be a link to a ZIP file if the puzzle has a non-pdf component. This content will be available at ``/protected/puzzles/{{puzzle_id}}/``. 
    - "Solution Link" should be a link to the PDF of the solution for the puzzle. If populated, this PDF will be available on the puzzle page after the hunt ends.
    - Note: checking the "Is html puzzle" box will ignore the PDF link, and redirect the puzzle link to the resources folder. This means that the unzipped resources folder must act as a complete web page (including an index.html page) and it is recommended to use all local URL references in your HTML.  

After filling out the page, hit "Save and add another" and continue to add puzzles until you have added all of the puzzles for the hunt. This will take a while, my recommendations are to be patient and have the unlocking graph on hand.

Create Auto-Response Objects
============================

This section is completely optional, but will make your life easier once the hunt is running. At the moment, whenever a user has submitted a correct answer, the server will respond "Correct!" and whenever the user submits a wrong answer the server will respond "Wrong Answer". 

Often you will want additional customized responses that can do anything from tell the user how they are wrong to tell them to "Keep going!". All you have to do is to go back into the edit page for a specific puzzle and enter regexes and response texts in the response boxes at the bottom of the page. 

Some notes about the responses:

  - Regexes are in python syntax
  - You are allowed to regex upon the correct answer and override the default "Correct!" response, the puzzle will still be marked as solved
  - Regexes are currently applied in no guaranteed order, answers that satisfy more than one regex will result in undefined behavior
  - Response texts are allowed to contain markdown style links: [foo](https://link.to.foo)

Create Prepuzzle Objects
========================

As of version 3.3.0, the server now supports prepuzzles. A prepuzzle is a simpler puzzle that exists outside of the normal set of puzzles for a hunt. Prepuzzles are different in a number of ways:

- Prepuzzles do not require users to sign in
- Once published, prepuzzles are accessable before the hunt is open
- Prepuzzle submissions only support auto-response and do not show up on the queue page
- Prepuzzles can be, but do not need to be tied to any specific hunt.

Like other above objects, to create a prepuzzle object, navigate to the prepuzzle section of the admin pages and click the "+" icon in the upper right.

Fill out the following fields:

- Puzzle name: Pretty self descriptive
- Released: Controls whether or not non-staff members can see the puzzle
- Hunt: Select which hunt this prepuzzle is associated with, leave blank to not associate it with any hunt.
- Answer: Pretty self explanatory
- Template: See the "Prepuzzle Templating" section below
- Resource link: Allows the optional inclusion of static files for the prepuzzle, must be a link to a ZIP file. See the "Prepuzzle Templating" section for details on how to reference the files.
- Response string: The string that the server sends back to the prepuzzle page when the puzzle is solved. In the simple example, this string is just displayed to the user, but more complex templates could do anything they desire with this string. 
- Puzzle URL: This isn't really a field but rather an easy way to copy out the prepuzzle URL because it isn't currently accessible from anywhere on the site. 

Prepuzzle Templating
--------------------

As with the hunt "Template" field, everything typed into the "Template" form on the hunt editing page will be run through django's templating engine and rendered as HTML. 

The following context will be passed to the renderer for use in the template: ``{'puzzle': ... }`` where 'puzzle' is the current prepuzzle object with the above accessible fields.

**While you may use completely custom HTML, it is STRONGLY RECOMMENDED that you add onto the default prepuzzle template (which extends prepuzzle.html) to get nice features like the header bar, common style sheets, google analytics, and javascript helper functions.**

A few notes about extending the default prepuzzle template:

- Put all of your additions inside the "content" block unless specified otherwise below.
- Do any style sheet or JS loading you need to do inside of an "includes" block as mentioned above in the hunt section.
- If you want to have simple answer checking and response, just use ``{% include "prepuzzle_answerbox.html" %}`` which will insert a submission box (and associated javascript) into the page and display the response string when the correct answer is entered.
- If you opt not to use the puzzle answerbox template, you can use the supplied javascript helper function "check_answer" which takes a callback that will be passed the response and the user's answer
- If you have supplied a resource_link that links to a zip file, after downloading from the management page, the files inside the zip file will be accessible using the the prepuzzle static tag: ``{% prepuzzle_static %}file.png``

Update Current Hunt Label
=========================

Congratulations! You have finished creating a hunt, head over to ``{server URL}/staff/management/`` and click the "Set Current" button next to your new hunt. This will cause it to become the hunt shown on the staff pages such as the Progress and Queue pages, it will be displayed on the homepage as the "Upcoming hunt", and it will be open to team registration. If any of those sound like things you don't want yet, you can wait as long as you want to set the hunt as the current hunt.
