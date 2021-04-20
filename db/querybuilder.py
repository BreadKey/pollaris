from datetime import datetime
from typing import Any, List, Type, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum


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
    query = f"select "

    if (not fields or len(fields) == 0):
        query += "*"
    else:
        query += ", ".join(fields)

    query += f" from {__buildTable(model)}"

    query += __buildWhere(where, encrypt)

    if (orderBy and len(orderBy) > 0):
        query += " order by " + \
            __buildField(orderBy[0]) + " " + orderBy[1].name

    if (limit):
        query += f" limit {limit}"

    return query


def insert(model: Type, data: dict, encrypt: dict = None) -> str:
    query = "insert into " + __buildTable(model)

    fields = []
    values = []

    for field, value in data.items():
        fields.append(__buildField(field))
        values.append(__buildValue(
            value, __getEncryptMethod(encrypt, field)))

    query += "(" + ", ".join(fields) + ") values(" + ",".join(values) + ")"

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
    if (where and len(where) > 0):
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


def __buildField(attribute: str) -> str:
    return f"`{attribute}`" if attribute == "index" else attribute


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
