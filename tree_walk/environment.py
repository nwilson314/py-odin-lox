from __future__ import annotations
from typing import Any

from token_type import Token
from error import RunTimeError

class Environment:
    def __init__(self, enclosing: Environment | None = None):
        self.values = {}
        self.enclosing = enclosing

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing != None:
            return self.enclosing.get(name)
        raise RunTimeError(name, f"Undefined variable '{name.lexeme}' during get.")

    def get_at(self, distance: int, name: str) -> Any:
        return self.ancestor(distance).values[name]

    def ancestor(self, distance: int) -> Environment:
        environment = self
        for _ in range(distance):
            environment = environment.enclosing
        return environment

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing != None:
            self.enclosing.assign(name, value)
            return
        raise RunTimeError(name, f"Undefined variable '{name.lexeme}' during assignment.")

    def assign_at(self, distance: int, name: Token, value: Any) -> None:
        self.ancestor(distance).values[name.lexeme] = value