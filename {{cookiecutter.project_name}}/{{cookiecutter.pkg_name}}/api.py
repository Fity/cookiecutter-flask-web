import functools

from flask import Blueprint, Response, Flask, json, request
from flask_sqlalchemy import Pagination
from typing import Optional, List

from mypy_extensions import TypedDict

from .cors import append_cors_header
from voluptuous import Schema, Invalid, REMOVE_EXTRA


class ApiResult:
    def __init__(self, value, status=200, next_page=None):
        self.value = value
        self.status = status
        self.nex_page = next_page

    def to_response(self):
        return Response(
            json.dumps(self.value, ensure_ascii=False),
            status=self.status,
            mimetype="application/json",
        )


class ErrorDict(TypedDict):
    message: str
    code: int


class ApiException(Exception):
    code: Optional[int] = None
    message: Optional[str] = None
    errors: Optional[List[ErrorDict]] = None

    status = 400

    def __init__(self, message, status=None, code=None, errors=None):
        self.message = message or self.message
        self.status = status or self.status
        self.code = code or self.code
        self.errors = errors or self.errors

    def to_result(self):
        rv = {"message": self.message}
        if self.errors:
            rv["errors"] = self.errors
        if self.code:
            rv["code"] = self.code
        return ApiResult(rv, status=self.status)


class NotAuthorized(ApiException):
    status = 401


class NotFound(ApiException):
    status = 404
    message = "resource not found"


class InvalidToken(ApiException):
    pass


class AuthExpired(ApiException):
    pass


class ApiFlask(Flask):
    def make_response(self, rv):
        if rv is None:
            rv = {}
        if isinstance(rv, Pagination):
            rv = {
                "pages": rv.pages,
                "has_prev": rv.has_prev,
                "has_next": rv.has_next,
                "total": rv.total,
                "items": rv.items,
            }
        from .globals import db

        if isinstance(rv, db.Model):
            rv = rv.as_dict()
        if isinstance(rv, (dict, list)):
            rv = ApiResult(rv)
        if isinstance(rv, ApiResult):
            response = rv.to_response()
        else:
            response = super(ApiFlask, self).make_response(rv)
        append_cors_header(response)
        return response


class ApiBlueprint(Blueprint):
    def post(self, rule, **options):
        options.pop("methods", None)
        return self.route(rule, methods=["POST"], **options)

    def get(self, rule, **options):
        options.pop("methods", None)
        return self.route(rule, **options)

    def put(self, rule, **options):
        options.pop("methods", None)
        return self.route(rule, methods=["PUT"], **options)

    def delete(self, rule, **options):
        options.pop("methods", None)
        return self.route(rule, methods=["DELETE"], **options)

    def patch(self, rule, **options):
        options.pop("methods", None)
        return self.route(rule, methods=["PATCH"], **options)


def dataschema(schema, required=False, extra=REMOVE_EXTRA, source="json"):
    if source == "args":
        required = False
    if isinstance(schema, dict):
        schema = Schema(schema, required, extra)

    def decorator(f):
        @functools.wraps(f)
        def new_func(*args, **kwargs):
            try:
                if source == "args":
                    data = request.args.to_dict()
                else:
                    data = request.get_json(silent=True) or {}
                kwargs.update(schema(data))
            except Invalid as e:
                raise ApiException(
                    "缺少入参字段:{}".format(".".join(str(path) for path in e.path))
                )
            return f(*args, **kwargs)

        return new_func

    return decorator


arg_dataschema = functools.partial(dataschema, source="args")
