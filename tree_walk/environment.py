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