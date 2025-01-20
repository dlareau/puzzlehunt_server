[![Build Status](https://travis-ci.org/dlareau/puzzlehunt_server.svg?branch=master)](https://travis-ci.org/dlareau/puzzlehunt_server)
[![Coverage Status](https://coveralls.io/repos/github/dlareau/puzzlehunt_server/badge.svg)](https://coveralls.io/github/dlareau/puzzlehunt_server)

# puzzlehunt_server [Archive]
## Note! This project has been deprecated in favor of [PuzzleSpring](https://github.com/dlareau/puzzlespring).
Please consider using PuzzleSpring instead of this project for new setups. It is more flexible, easier to get started with, and will see regular updates. A migration script for those who have already deployed puzzlehunt_server will be be released alongside PuzzleSpring 1.0.


## Old Description
A server for running puzzle hunts. This project is mainly used by Puzzlehunt CMU to run their puzzlehunt, but is generic enough to be used for nearly any puzzle hunt. Includes basic features such as per-puzzle pages, automatic answer response, teams, customizable unlocking structure, and admin pages to manange submissions, teams, as well as hunt progress. It also includes automatic team creation from registration, privacy settings for hunts, cool charts, a built in chat, and automatic file fetching and hosting.

Documentation can be found at http://docs.puzzlehunt.club

If you are interested in getting this running elsewhere, let me (dlareau@cmu.edu) know. I'd be happy to help anyone who wants to get this up and running for their needs, and get help get you over any gaps in setup documentation. I'd also recommend if possible waiting for version 4.1 which will make adapting this software to other hunts easier: https://github.com/dlareau/puzzlehunt_server/issues/121

Please submit issues for any bugs reports or feature requests.

### Setup
This project now uses docker-compose as it's main form of setup. You can use the following steps to get a sample server up and going

1. Install [docker/docker-compose.](https://docs.docker.com/compose/install/)
2. Clone this repository.
3. Make a copy of ```sample.env``` named ```.env``` (yes, it starts with a dot).
4. Edit the new ```.env``` file, filling in new values for the first block of uncommented lines. Other lines can be safely ignored as they only provide additional functionality.
5. Run ```docker-compose up``` (possibly prepending ```sudo``` if needed)
6. Once up, you'll need to run the following commands to collect all the static files (to be run any time you alter static files) and to load in an initial hunt to pacify some of the display logic (to be run only once) :
```
docker-compose exec app python3 /code/manage.py collectstatic --noinput
docker-compose exec app python3 /code/manage.py loaddata initial_hunt
```
7. You should now have the server running on a newly created VM, accessible via [http://localhost](http://localhost). The repository you cloned has been linked into the VM by docker, so any changes made to the repository on the host system should show up automatically. (A ```docker-compose restart``` may be needed for some changes to take effect)
