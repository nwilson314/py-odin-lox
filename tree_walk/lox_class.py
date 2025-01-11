from __future__ import annotations
from typing import Any, TYPE_CHECKING

from error import RunTimeError
from token_type import Token
from lox_callable import LoxCallable, LoxFunction

if TYPE_CHECKING:
    from interpreter import Interpreter


class LoxClass(LoxCallable):
    def __init__(self, name: str, superclass: LoxClass, methods: dict[str, LoxCallable]):
        self.methods = methods
        self.name = name
        self.superclass = superclass
    
    def __str__(self):
        return self.name

    def call(self, intrepreter: 'Interpreter', arguments: list[Any]) -> Any:
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer != None:
            initializer.bind(instance).call(intrepreter, arguments)
        return instance

    def find_method(self, name: str) -> LoxFunction | None:
        if name in self.methods:
            return self.methods[name]
        
        if self.superclass is not None:
            return self.superclass.find_method(name)

    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer == None:
            return 0
        return initializer.arity()


class LoxInstance:
    def __init__(self, klass: LoxClass):
        self.klass = klass
        self.fields: dict[str, Any] = {}

    def __str__(self):
        return f"{self.klass} instance"

    def get(self, name: Token) -> Any:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method != None:
            return method.bind(self)

        raise RunTimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: Any) -> None:
        self.fields[name.lexeme] = value