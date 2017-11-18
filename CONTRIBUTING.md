To start contributing to this project just post an issue to tell what you want to work on and if no one's already working on it you can proceed.
Look into the *TODO.txt* for topics we think we need to work on though you are free to think of any different idea and work on it.

## Steps for setting the project up:

1. Clone the repo. In the parent directory of the repo create a python3 virtualenv for the project.
   ("sudo apt-get install virtualenv", "virtualenv python=python3 venv_locus")
   Source into the virtualenv (terminal: "source <venv>/bin/activate"). cd into repo and do:
   "pip install -r requirements.txt" to install all the needed python packages.
2. To test the project cd into the repo and do "python manage.py runserver" and open the browser with the url
   and port mentioned in the terminal after starting the test server.
3. When you are editing the code and new python packages are installed (make sure to do so while running inside the
   virtualenv), update the requirements.txt by running "pip freeze >> requirements.txt". Every time new packages are
   added by some other team member which isn't present in your virtualenv, run "pip install -r requirements.txt"
4. When changes to the database schema are made (the models), run "python manage.py makemigrations" and then "python manage.py migrate" from the repo directory in order to make the corresponding changes in the schema
   to your local database. (mostly not needed at the moment as we are using sqlite3 rn)
5. When stable changes have been made to the project, push it to the main directory by following these steps:
	i. git add .
	ii. git commit -m "<comment about the changes>"
	iii. git push origin master (if changing in the master branch)
   To pull changes from the master branch into your repo:
	git pull
