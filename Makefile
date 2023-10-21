venv: venv/bin/activate

venv/bin/activate: requirements.txt
	find . -regex '*.pyc' -delete;
	test -d venv || python3 -m venv venv
	. venv/bin/activate; pip3 install  --ignore-installed -Ur requirements.txt
	touch venv/bin/activate

init: venv
	. venv/bin/activate

test: init
	. venv/bin/activate ; python3 manage.py test --pattern="*test*"

run: venv
	. venv/bin/activate ; find -iname "*.pyc" -delete; python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000

makemigrations: init
	. venv/bin/activate ; python3 manage.py makemigrations

makemigrations-merge: init
	. venv/bin/activate ; python3 manage.py makemigrations --merge

migrate: init
	. venv/bin/activate ; python3 manage.py migrate

execute: venv
	. venv/bin/activate; $(command)

createsuperuser: init
	. venv/bin/activate ; python3 manage.py createsuperuser


collectstatic: init
	. venv/bin/activate ; python3 manage.py collectstatic --noinput

startapp: init
	. venv/bin/activate ; python3 manage.py startapp $(appname)
#./run-make.sh startapp appname=bus

clean:
	rm -rf venv
	find -iname "*.pyc" -delete

shell: init
	. venv/bin/activate ; python3 manage.py shell

dumpdataxml: init
	. venv/bin/activate ; python3 manage.py dumpdata --natural-foreign --traceback --indent 2 --format xml > db.xml
#./run-make.sh dumpdataxml

loaddataaxml: init
	. venv/bin/activate ; python3 manage.py loaddata db.xml
#./run-make.sh loaddataaxml

.PHONY: clean execute
