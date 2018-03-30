How to Create a Hunt
********************

Below are all of the steps you should need to take to create a puzzlehunt and have it ready to run:

Create Hunt Object
==================

You aren't going to get very far without a hunt object to attach all of this data to, so sign in with a staff account and navigate over to ``{server URL}/admin/huntserver/hunt/``

Click the "Add Hunt" button at the top. 

You will be brought to the hunt creation page, which you should fill out, keeping in mind the following points:

  - Make sure the start date is accurate or at the very least in the future, otherwise people will be able to see your hunt immediately.
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

As of version ``3.0.0``, in order to reduce repository clutter, it is now against policy to commit files specific to a certain hunt to the respository. This means that you are no longer allowed to put images, fonts, and other files in ``/huntserver/static`` or ``/static``. To still allow the use of new static files in each hunt, a new object class has been created called "Hunt Asset Files". This class allows uploading of assets from the web interface, removing the need to interact with the hosting server directly.

To upload a new asset file, navigate to ``{server URL}/admin/huntserver/huntassetfile/`` and click the blue "Add hunt asset file" button at the top. On the following screen, choose the file you wish to upload and hit save. Keep in mind that the URL for the file will be generated based on the uploaded file name and cannot be changed once uploaded, so name your files beforehand.

After you upload your file, click the save button and you will be taken back to the list of asset files. Next to each asset file is the link to use in your html template to access that file. It is clear to see that for each file, the link is just ``/media/hunt/assets/{name of file}``.

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

While you may have all of the information you need, that doesn't mean you know what to do with it. Below is a simple example base upon our first hunt. It will show the puzzles, display the answer for any solved puzzles, and demonstrates how to insert a break a hunt into two rounds.

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

Start by going to ``{server URL}/admin/huntserver/puzzle/`` and clicking the "New Puzzle" button at the top. 

You will be brought to the puzzle creation page, which you should fill out, keeping in mind the following points:

  - Puzzle number should ideally be incremental starting at 1, this will be used for ordering puzzles
  - Puzzle ID should be unique across all puzzles ever made, and it is good practice to have the last two digits match the puzzle number
  - Link should be a publicly accessible PDF link (including https://) that doesn't require any authentication to access
  - You don't need to fill in num pages, the server will do that for you upon downloading
  - Num required to unlock represents the number of puzzles in the below list that need to be solved to unlock this puzzle. Any puzzle with a '0' here will be considered part of the initial set
  - Don't worry about "Responses" right now, we'll talk about that below.

After filling out the page, hit "Save and add another" and continue to add puzzles until you have added all of the puzzles for the hunt. This will take a while, my recommendations are to be patient and have the unlocking graph on hand.

Create Auto-Response Objects
============================

This section is completely optional, but will make your life easier once the hunt is running. At the moment, whenever a user has submitted a correct answer, the server will respond "Correct!" and whenever the user submits a wrong answer the server will respond "Wrong Answer". 

Often you will want additional customized responses that can do anything from tell the user how they are wrong to tell them to "Keep going!". All you have to do is to go back into the edit page for a specific puzzle and enter regexes and response texts in the response boxes at the bottom of the page. 

Some notes about the responses:

  - Regexes are in python syntax
  - You are allowed to regex upon the correct answer and override the default "Correct!" response, the puzzle will still be marked as solved
  - Regexes are currently applied in no guaranteed order, answer that satisfy more than one regex are considered undefined behavior
  - Response texts are allowed to contain markdown style links: [foo](https://link.to.foo)

Update Current Hunt Label
=========================

Congratulations! You have finished creating a hunt, head over to ``{server URL}/staff/management/`` and click the "Set as Current" button next to your new hunt. This will cause it to become the hunt represented by the staff pages such as the Progress and Queue pages, it will be displayed on the homepage as the "Upcoming hunt", and it will be open to team registration. If any of those sound like things you don't want yet, you can wait as long as you want to set the hunt as the current hunt.
