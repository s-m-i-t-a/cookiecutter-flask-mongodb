===============================
{{ cookiecutter.project_name }}
===============================

{{ cookiecutter.project_short_description}}


Quickstart
----------

::

    git clone https://{{cookiecutter.git_provider}}/{{cookiecutter.git_username}}/{{ cookiecutter.repo_name }}
    cd {{cookiecutter.repo_name}}
    pip install -r requirements/dev.txt
    APP_CONFIGURATION="Development" python {{cookiecutter.repo_name}}/manage.py runserver
