from __future__ import annotations
from abc import ABC, abstractmethod
from decimal import Decimal
from time import time
from typing import Any, TYPE_CHECKING

from error import ReturnError
from environment import Environment
from stmt import Function

if TYPE_CHECKING:
    from interpreter import Interpreter
    from lox_class import LoxInstance

class LoxCallable(ABC):
    @abstractmethod
    def call(self, interpreter: 'Interpreter', arguments: list[Any]) -> Any:
        pass

    @abstractmethod
    def arity(self) -> int:
        pass


class Clock(LoxCallable):
    def __init__(self):
        self.start_time = time()
    
    def arity(self) -> int:
        return 0
    
    def call(self, interpreter: 'Interpreter', arguments: list[Any]) -> Any:
        return Decimal(time() - self.start_time)
    
    def __str__(self) -> str:
        return "<native fn 'clock'>"


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function, closure: Environment, is_initializer: bool = False):
        self.is_initializer = is_initializer
        self.closure = closure
        self.declaration = declaration


    def arity(self) -> int:
        return len(self.declaration.params)

    def bind(self, instance: 'LoxInstance'):
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)

    def call(self, interpreter: 'Interpreter', arguments: list[Any]) -> Any:
        environment = Environment(self.closure)

        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnError as return_value:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return return_value.value

        if self.is_initializer:
            return self.closure.get_at(0, "this")
        return None

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"