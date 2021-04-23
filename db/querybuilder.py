from datetime import datetime
from typing import Any, List, Type, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import re


class Order(Enum):
    Desc = "desc"
    Asc = "asc"


@dataclass
class Expression:
    field: Union[str, 'Expression']
    value: Any
    operator: str = "="
    needBracket: bool = False


def select(model: Type, fields: List[str] = None,
           where: List[Expression] = None,
           encrypt: dict = None,
           orderBy: Tuple[str, Order] = None,
           limit: int = None) -> str:
    query = "select "

    query += "*" if not fields else ", ".join(
        [__buildField(field) for field in fields])

    query += f" from {__buildTable(model)}"

    query += __buildWhere(where, encrypt)

    if (orderBy):
        query += " order by " + \
            __buildField(orderBy[0]) + " " + orderBy[1].name

    if (limit):
        query += f" limit {limit}"

    return query


def insert(model: Type, data: dict, encrypt: dict = None, onDuplicate: Expression = None) -> str:
    query = "insert into " + __buildTable(model)

    fields = []
    values = []

    for field, value in data.items():
        fields.append(__buildField(field))
        values.append(__buildValue(
            value, __getEncryptMethod(encrypt, field)))

    query += "(" + ", ".join(fields) + ") values(" + ", ".join(values) + ")"

    if (onDuplicate):
        query += " on duplicate key update " + __express(onDuplicate, encrypt)

    return query


def update(model: Type, data: dict, where: List[Expression] = None, encrypt: dict = None) -> str:
    query = "update " + __buildTable(model)

    query += " set "
    sentences = []
    for field, value in data.items():
        sentence = __buildField(field) + " = "
        if isinstance(value, Expression):
            sentence += __express(value, encrypt)
        else:
            sentence += __buildValue(value, __getEncryptMethod(encrypt, field))
        sentences.append(sentence)

    query += ", ".join(sentences)
    query += __buildWhere(where, encrypt)

    return query


def delete(model: Type, where: List[Expression] = None, encrypt: dict = None):
    query = "delete from " + __buildTable(model)

    query += __buildWhere(where, encrypt)

    return query


def __buildWhere(where: List[Expression], encrypt: dict) -> str:
    query = ""
    if where:
        query += " where "
        sentences = []
        for expression in where:
            sentences.append(
                __express(expression, encrypt))

        query += " and ".join(sentences)

    return query


def __buildTable(model: Type) -> str:
    table = model.__name__

    if (table[-2:] in ["ty"]):
        return table[:-1] + "ies"

    return table + 's'


def __express(expression: Expression, encrypt: dict = None) -> str:
    field = __express(expression.field, encrypt) if isinstance(
        expression.field, Expression) else __buildField(expression.field)
    value = __express(expression.value, encrypt) if isinstance(expression.value, Expression) else __buildValue(
        expression.value, __getEncryptMethod(encrypt, expression.field))

    sentence = field + f" {expression.operator} " + value

    return "(" + sentence + ")" if expression.needBracket else sentence


def __buildField(field: str) -> str:
    return f"`{field}`" if re.fullmatch(r"index|key", field) else field


def __buildValue(value: Any, encryptMethod: str = None) -> str:
    if value is None:
        return "null"

    v = value.isoformat() if isinstance(value, datetime) else value
    v = v.name if isinstance(v, Enum) else v
    v = int(v) if isinstance(v, bool) else v
    v = f'"{v}"' if isinstance(v, str) else v.__str__()

    if (encryptMethod):
        v = encryptMethod + "(" + v + ")"

    return v


def __getEncryptMethod(encrypt: dict, field: str) -> str:
    if (encrypt):
        return encrypt.get(field)
    return None
