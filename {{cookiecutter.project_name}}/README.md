# {{cookiecutter.project_name}}

{{cookiecutter.project_description}}

### features

1. simple validation
2. rest api friendly
3. basic jwt auth with different audience
4. sqalchemy integrated

### install pdm

    pip3 install pdm

### install requirements

    pdm install

### running

0. there is a sample .flaskenv for you. modity it according to your project.
1. add APP_SETTINGS={your actual yaml config path} to your .env/.flaskenv file, APP_SETTINGS=config.yml is a good default choice.
2. `config.yml.example` is a minimal example with db config for you. `cp config.yml.example config.yml`
3. add `FLASK_APP={{ cookiecutter.pkg_name }}.main:app` and `FLASK_DEBUG=1` to your .env/.flaskenv file
4. `pdm run flask db init`
5. `pdm run flask db migrate -m 'init db'
6. `pdm run flask db upgrade`. Note, this will update your database to match your models. Use it only in your local environment. Never use in prod.
7. [OPTIONAL] `pdm run flask ishell` or `pdm run ishell`. You will get a debugging IPython shell with a basic `app`.
8. `pdm run flask run` or `pdm run start`
