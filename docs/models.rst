Models
******

Hunt
----
    This is the object that contains basic details about a puzzlehunt and serves as the main point of connection for many models related to the hunt. A hunt has the following attibutes:

    - Hunt name (hunt_name)
        The name of the hunt as the public will see it. "Carnival Hunt" for example.

    - Hunt number (hunt_number)
        The number of the hunt, this is used internally for sorting and is forced to be unique between hunts. It is a good idea to have this just be one higher than the last hunt.

    - Team size (team_size)
        The number of people allowed on one team for the hunt. This is strictly enforced on the user side, but not from the admin side.

    - Start date (start_date)
        The datetime object corresponding to the start time and date of the hunt. This controls a number of things such as access to the main hunt page for normal users and other visibility related items. This is also the time and date displayed on the front page.

    - End date (end_date)
        Similar to start_date, this is the datetime object corresponding to the end time and date of the hunt. This controlls things like closing answer submission for normal users and after this time the hunt will be considered "public" meaning anyone (even users that aren't signed in) can see all of the puzzles.

    - Location (location)
        The string of where the hunt will be held. "Porter hall A100" for example.

    - Current hunt status (is_current_hunt)
        A boolean describing whether or not the hunt is the hunt currently being played. This controls many things such as which hunt is shown on the front page, which hunt is linked to in the menubar, and which teams are shown on the staff pages. Only one hunt may have this selected at any given time. Thankfully back end checks ensure that whenever it is set to true for one hunt, it is automatically set to false for all other hunts.

Puzzle
------
    This is the object that represents a puzzle within a hunt. Each puzzle has the following attributes:

    - Puzzle number (puzzle_number)
        The number of the puzzle within the given hunt. It should be unique to the hunt and should roughly correspond to the ordering in which puzzles will be presented throughout the hunt. Please keep these under 100 or so, the unlocking algorithm unfortunately uses space corresponding to the max puzzle number.

    - Puzzle name (puzzle_name)
        The name of the puzzle as it will be seen by the puzzle hunters.

    - Puzzle ID (puzzle_id)
        The puzzle ID that will be used to uniquely identify puzzles throughout various parts of the server. It can legally be anything, but ideally should be 3 characters in length containing only hexadecimal characters.

    - Puzzle answer (answer)
        The answer to the puzzle, should match exactly, regex not supported.

    - Link to puzzle PDF (link)
        A full link (starting with http(s)://) to the PDF of the puzzle. Should be accessible without any sort of authentication.

    - Number of puzzles required to unlock (num_required_to_unlock)
        This determines when a puzzle will be unlocked. When a team has solved num_required_to_unlock puzzles that list this puzzle in their unlocks field, the puzzle will unlock.

    - Puzzles that this puzzle unlocks (unlocks)
        Which puzzles does this puzzle work towards unlocking.

    - Hunt (hunt)
        The hunt object which this puzzle belongs to.

    - Length of PDF (num_pages)
        The length of the puzzle PDF in pages, you shouldn't need to set this, it will be automatically set when the PDF is downloaded.


Team
----
    This is the object that represents a team within a hunt. A team can only belong to one hunt, but team names don't have to be globally unique, so there could be a team with the same name in two different hunts. Each team has the following attributes:

    - Team name (team_name)
        The team name as will be seen in many places.

    - Puzzles the team has solved (solved)
        A many to many relationship describing all of the puzzles the team has solved. It uses the "solve" model as a through model for the relationship.

    - Puzzles the team has unlocked (unlocked)
        A many to many relationship describing all of the puzzles the team has unlocked. It uses the "unlock" model as a through model for the relationship.

    - Unlockable objects the team has unlocked (unlockables)
        A many to many relationship describing all of the unlockable objects the team has unlocked.

    - Hunt (hunt)
        The hunt which this team belongs to.

    - Team location (location)
        The team's location during the hunt as a simple string. "BH126A" for example. After registration, this should have one of three values: "has_a_room", "need_a_room", or "off_campus", as teams are not yet allowed to set their own location.

    - Team join code (join code)
        An up to 5 character code that other team members will have to enter to join a team (to prevent random people joining). When a team is created, a 5 character uppercase random alphanumeric code with confusing letter/number combos removed is generated automatically.

    - Is Playtestser (playtester)
        A boolean that indicates whether or not this team is a playtesting team. Playtesting teams get access to the hunt before it is released to the rest of the teams at the start date/time.


Person
------
    This is the object that represents the person associated with a user. Because we don't change the built in Django user model, we have this class for the purpose of associating additional information with each user. Each person has the following attributes:

    - Associated user (user)
        The user for this person model.

    - Phone number (phone)
        The person's phone number. There is not a consistent formatting at the moment for phone numbers. This is a user provided field.

    - Allergies (allergies)
        Any allergies the person has. This is a user provided field.

    - Misc Comments (comments)
        Any comments the person has for hunt staff. This is a user provided field.

    - Teams (teams)
        A relationship designating which teams this person is on. Behavior is unpredictable if a user is on more than one team per hunt, and joining more than one team per hunt is impossible from the user's view.

    - Is shibboleth account (is_shib_acct)
        A boolean for whether or not this account's authentication is done through shibboleth. This should not need to be edited, as it is set automatically if a user is created from a shibboleth sign in.


Submission
----------
    This is the object that represents a submission to a puzzle. Each submission has the following attributes:

    - Associated Team (team)
        The team object for the team that made this submission.

    - Submission Time (submission_time)
        The date/time that this submission was made.

    - Submission Text (submission_text)
        The text of the submission.

    - Response Text (response_text)
        The text of the staff response to the submission. An empty string means there has not been a response yet.

    - Associated Puzzle (puzzle)
        The puzzle object that this object is a submission to.

    - Date of last modification (modified_date)
        The date/time that this submission was last modified as staff is allowed to edit their response.

    There is one property of this class that is particularly useful. The "is_correct" property will return true if the submission is correct for the corresponding puzzle associated with this submission, and false otherwise.


Solve
-----
    This is the object that represents a puzzle solve. This model is the through model for team.solved. Each solve has the following attributes:

    - Associated Puzzle (puzzle)
        The puzzle that this solve object is for.

    - Associated Team (team)
        The team that solved the puzzle.

    - Associated Submission (submission)
        The correct submission that solved the puzzle.


Unlock
------
    This is the object that represents a puzzle unlock. This model is the through model for team.unlocked. Each unlock has the following attributes:

    - Associated Puzzle (puzzle)
        The puzzle that this unlock is for.

    - Associated Team (team)
        The team that unlocked the puzzle.

    - Unlock time (time)
        The time at which the puzzle was unlocked.

Message
-------
    This is the object that represents a message in the chat client. Each message has the following attributes:

    - Associated Team (team)
        The team that this message is associated with.

    - Is Response (is_response)
        A boolean indicating whether or not the message is a response to the team. At the moment, having this attribute be true is indicative of it being sent by a staff member.

    - Message Text(text)
        The text of the message. Should not include the "Name:" part of the message.

    - Message Time (time)
        The time the message was created.


Unlockable
----------
    This is the object that represents an unlockable object after finishing a puzzle. Each unlockable has the following attributes:

    - Associated Puzzle (puzzle)
        The puzzle that

    - Unlockable Content Type (content_type)

    - Unlockable Content(content)


Response
--------
    This is the object that represents an automatic response category to a submission. Each instance is a regex that will match on submissions to the specified puzzle and provide the given response. Each response has the following attributes:

    - Associated Puzzle (puzzle)

    - Response Regex (regex)

    - Response Text (text)
