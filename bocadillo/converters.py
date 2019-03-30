import decimal
import inspect
from datetime import date, datetime, time
from functools import wraps
from typing import Callable, Dict, List, Tuple, Type

import typesystem

from .errors import HTTPError

FIELD_ALIASES: Dict[Type, typesystem.Field] = {
    int: typesystem.Integer(),
    float: typesystem.Float(),
    bool: typesystem.Boolean(),
    decimal.Decimal: typesystem.Decimal(),
    date: typesystem.Date(),
    time: typesystem.Time(),
    datetime: typesystem.DateTime(),
}


class Converter:
    def __init__(self, func: Callable):
        self.func = func
        self.signature = inspect.signature(self.func)

        self.annotations: Dict[str, Type] = {
            param.name: param.annotation
            for param in self.signature.parameters.values()
            if param.annotation is not inspect.Parameter.empty
        }

    def convert(self, args: tuple, kwargs: dict) -> Tuple[tuple, dict]:
        bound: inspect.BoundArguments = self.signature.bind(*args, **kwargs)
        bound.apply_defaults()

        errors: List[typesystem.ValidationError] = []

        for key, value in bound.arguments.items():
            try:
                annotation = self.annotations[key]
            except KeyError:
                continue

            field: typesystem.Field
            if isinstance(annotation, typesystem.Field):
                field = annotation
            else:
                field = FIELD_ALIASES.get(annotation)
                if field is None:
                    continue

            # NOTE: don't use `field.validate()` directly. Use an `Object`
            # so that error messages contain the name of the field
            # as passed to `.validate()` below.
            validator = typesystem.Object(properties=field)

            try:
                validated = validator.validate({key: value})
            except typesystem.ValidationError as exc:
                errors.extend(exc.messages())
            else:
                bound.arguments[key] = validated[key]

        if errors:
            raise typesystem.ValidationError(messages=errors)

        return bound.args, bound.kwargs


class ViewConverter(Converter):
    def __init__(self, func):
        super().__init__(func)

        self.query_parameters = {
            param.name: param.default
            for param in self.signature.parameters.values()
            if param.default is not inspect.Parameter.empty
        }

    def get_query_params(self, args, kwargs):
        raise NotImplementedError

    def convert(self, args, kwargs):
        query_params = self.get_query_params(args, kwargs)

        for name, default in self.query_parameters.items():
            kwargs[name] = query_params.get(name, default)

        return super().convert(args, kwargs)


def convert_arguments(func: Callable, converter_class=None) -> Callable:
    if converter_class is None:
        converter_class = Converter

    converter = converter_class(func)

    @wraps(func)
    async def converted(*args, **kwargs):
        args, kwargs = converter.convert(args, kwargs)
        return await func(*args, **kwargs)

    return converted


async def on_validation_error(req, res, exc: typesystem.ValidationError):
    raise HTTPError(400, detail=dict(exc))
