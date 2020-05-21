import importlib
import inspect
import itertools
import os
import yaml
import logging
import traceback
import pkgutil

from flask import request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
from werkzeug.routing import RequestRedirect
from werkzeug.utils import redirect

from .api import ApiException, ApiFlask
from .globals import db, migrate


def class_scanner(pkg, filter_=lambda _: True):
    """
    :param pkg: a module instance or name of the module
    :param filter_: a function to filter matching classes
    :return: all filtered class instances
    """

    def scan_pkg_file(pkg):
        return {
            cls[1]
            for cls in inspect.getmembers(pkg, inspect.isclass)
            if filter_(cls[1])
        }

    if isinstance(pkg, str):
        pkg = importlib.import_module(pkg)
    if not hasattr(pkg, "__path__"):
        return scan_pkg_file(pkg)
    classes = scan_pkg_file(pkg)
    for _, modname, _ in pkgutil.iter_modules(pkg.__path__):
        module = importlib.import_module("." + modname, pkg.__name__)
        classes |= class_scanner(module, filter_)
    return classes


def scan_models():
    from {{cookiecutter.pkg_name}}.globals import Model

    models = {}
    for exc_class in itertools.chain(
        class_scanner("{{cookiecutter.pkg_name}}.models", lambda exc: issubclass(exc, Model))
    ):
        models[exc_class.__name__] = exc_class
    return models


def create_app(config=None):
    config = config or {}
    app = ApiFlask("{{ cookiecutter.pkg_name }}")
    app.config.from_object("{{cookiecutter.pkg_name}}.settings")
    config_path = os.environ.get("APP_SETTINGS", "config.yml")
    if os.path.exists(config_path):
        with open(config_path) as f:
            config.update(yaml.load(f, Loader=yaml.Loader))
    app.config.update(config)

    register_blueprints(app)
    scan_models()
    db.init_app(app)
    migrate.init_app(app, db)
    init_shell(app)

    register_error_handlers(app)
    return app


def create_api_app():
    pass


def create_normal_app():
    pass


def register_blueprints(app):
    for name in find_modules("{{cookiecutter.pkg_name}}.apps", include_packages=True):
    mod = importlib.import_module(name)
    if hasattr(mod, "bp"):
        app.register_blueprint(mod.bp)

    @app.after_request
    def reset_session(response):
        from .globals import session

        try:
            session.rollback()
        except BaseException:
            pass
        return response


def register_error_handlers(app):
    def wants_json_response():
        return (
            request.accept_mimetypes["application/json"]
            >= request.accept_mimetypes["text/html"]
        )

    app.register_error_handler(ApiException, lambda err: err.to_result())

    logger = logging.getLogger(__name__)

    def handle_err(e):
        if wants_json_response():
            if isinstance(e, BadRequest):
                return ApiException(e.description).to_result()
            if isinstance(e, NotFound):
                return ApiException("Not Found", status=404).to_result()
            if isinstance(e, MethodNotAllowed):
                return ApiException("method not allowed", status=405).to_result()
            logger.exception("系统异常")
            if app.debug:
                return ApiException(traceback.format_exc(), status=500).to_result()
            return ApiException("系统异常", status=500).to_result()
        if isinstance(e, NotFound):
            return "resource not found", 404
        if isinstance(e, MethodNotAllowed):
            return "method not allowed", 405
        if isinstance(e, RequestRedirect):
            return redirect(e.new_url)
        raise e

    app.register_error_handler(Exception, handle_err)

    app.register_error_handler(ApiException, lambda err: err.to_result())


def init_shell(app):
    @app.cli.command("ishell")
    def shell():
        # lazy import these modules as they are only used in the shell context
        from IPython import embed, InteractiveShell
        import cProfile
        import pdb

        main = importlib.import_module("__main__")

        banner = f"App: {{cookiecutter.pkg_name}}"
        from . import models

        ctx = main.__dict__
        ctx.update(
            {**models.__dict__, "session": db.session, "pdb": pdb, "cProfile": cProfile}
        )

        with app.app_context():
            ctx.update(app.make_shell_context())
            InteractiveShell.colors = "Neutral"
            embed(user_ns=ctx, banner2=banner)
