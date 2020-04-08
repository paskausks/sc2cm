# SC2CM

**The project is very, very abandoned ☹️**

A Django application for convienently managing a Starcraft 2 clan.

## Requirements
* Python 3.5+
* Django 1.8+

## Installation
Installation instructions are for computers running on GNU/Linux.

Clone the repository and put the `sc2clanman` folder somewhere in your `PYTHONPATH`.

Install dependencies:
```bash
$ pip install -r requirements.txt
```

In your Django project's settings.py:
* Add `sc2clanman` to your `INSTALLED_APPS`.
* Add your Battle.net API key (get it at https://dev.battle.net/ if you don't have one already), clan tag and clan's verbose name:
```python
# SC2 clan manager settings
SC2_CLANMANAGER_BNET_API_KEY = 'superdupersecret'
SC2_CLANMANAGER_CLAN_TAG = 'SKT1'
SC2_CLANMANAGER_CLAN_VERBOSE_NAME = 'SK Telecom T1'
```

Run the initial sync jobs:
```bash
$ python manage.py syncmembers && python manage.py syncmemberdetails
```

Add cronjobs so your data is up to date. Edit your crontab with `crontab -e` and add the following entries
```bash
# Syncs for sc2clanmanager need to run with bash
SHELL=/bin/bash

# Update member statuses each 30 minutes and update members each 24 hours.
0,30 * * * * source <path-to-your-virtualenv>/bin/activate && python <path-to-django-project>/manage.py syncmemberdetails; deactivate
20 4 * * * source <path-to-your-virtualenv>/bin/activate && python <path-to-django-project>/manage.py syncmembers; deactivate

```
If you don't use virtualenvs, ommit the modification of the `SHELL` environment variable and the `source` and `deactivate` commands.

Add an URL route to your project's urls.py:
```python
urlpatterns = [
    ...
    url(r'^sc2cm/', include('sc2clanman.urls')),
]
```

Run migrations:
```bash
$ python manage.py makemigrations && python manage.py migrate
```
