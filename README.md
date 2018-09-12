[![Build Status](https://travis-ci.org/dlareau/puzzlehunt_server.svg?branch=tests)](https://travis-ci.org/dlareau/puzzlehunt_server)
[![Coverage Status](https://coveralls.io/repos/github/dlareau/puzzlehunt_server/badge.svg?branch=tests)](https://coveralls.io/github/dlareau/puzzlehunt_server?branch=tests)

# puzzlehunt_server
Server for Puzzlehunt CMU's bi-annual puzzlehunt. Includes basic features such as per-puzzle pages, automatic answer response, teams, customizable unlocking structure, and admin pages to manange submissions, teams, as well as hunt progress. It also includes automatic team creation from registration, privacy settings for hunts, cool charts, a built in chat, and automatic file fetching and hosting. 

Documentation can be found at http://docs.puzzlehunt.club

While there is fairly large amount of configuration making this specific to Puzzlehunt CMU, if you are interested in getting this running elsewhere, let me know. I'd be happy to help anyone who wants to get this up and running for their needs. 
	
Please submit issues for any bugs reports or feature requests.

### Super simple setup
If you just want to get started developing or want to stand up a simple test server and don't care about security, you can follow the following steps:

1. Install [Virtualbox.](https://www.virtualbox.org/wiki/Downloads)
2. Install [Vagrant.](https://www.vagrantup.com/downloads.html)
3. Make a folder for the VM.
4. Clone this repository into that folder. (such that the folder you made now contains only one folder named "puzzlehunt_server")
5. Copy the Vagrantfile from the config folder within the puzzlehunt_server folder out into the folder that you made.
6. Run "vagrant up" from the folder you made and wait for it to complete.
7. You should now have the server running on a newly created VM, accessible via [http://localhost:8080](http://localhost:8080). The repository you cloned has been linked into the VM by vagrant, so any changes made to the repository on the host system should show up automatically. (A "vagrant reload" may be needed for some changes to take effect)