# {{cookiecutter.project_name}}

{{cookiecutter.project_description}}

### features

1. simple validation
2. rest api friendly
3. basic jwt auth with different audience
4. sqalchemy integrated

### install poetry

    pip3 install poetry

### install requirements

    poetry install

### running

0. there is a sample .flaskenv for you. modity it according to your project.
1. add APP_SETTINGS={your actual yaml config path} to your .env/.flaskenv file, APP_SETTINGS=config.yaml is a good default choice.

1. add `FLASK_APP={{ cookiecutter.pkg_name }}.main:app` and `FLASK_DEBUG=1` to your .env/.flaskenv file

1. flask ishell

5) poetry run pytest tests

6) `poetry run flask run` or `poetry shell && flask run`
