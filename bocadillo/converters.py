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


def convert_arguments(func: Callable) -> Callable:
    sig = inspect.signature(func)

    annotations: Dict[str, Type] = {
        param.name: param.annotation
        for param in sig.parameters.values()
        if param.annotation is not inspect.Parameter.empty
    }

    def _convert(args: tuple, kwargs: dict) -> Tuple[tuple, dict]:
        bound: inspect.BoundArguments = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        errors: List[typesystem.ValidationError] = []

        for key, value in bound.arguments.items():
            try:
                field = FIELD_ALIASES[annotations[key]]
            except KeyError:
                pass
            else:
                try:
                    value = field.validate(value)
                except typesystem.ValidationError as exc:
                    errors.extend(exc.messages())
                else:
                    bound.arguments[key] = value

        if errors:
            raise typesystem.ValidationError(messages=errors)

        return bound.args, bound.kwargs

    if inspect.iscoroutinefunction(func):

        @wraps(func)
        async def converted(*args, **kwargs):
            args, kwargs = _convert(args, kwargs)
            return await func(*args, **kwargs)

    else:

        @wraps(func)
        def converted(*args, **kwargs):
            args, kwargs = _convert(args, kwargs)
            return func(*args, **kwargs)

    return converted


async def on_validation_error(req, res, exc: typesystem.ValidationError):
    raise HTTPError(400, detail=dict(exc))
