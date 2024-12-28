from types import ClassMethodDescriptorType
from token_type import Token, TokenType

class ParseError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class RunTimeError(RuntimeError):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.message = message
        self.token = token

class Error:
    had_error = False
    had_runtime_error = False

    @classmethod
    def error(cls, line: int, message: str):
        cls.report(line, "", message)

    @classmethod
    def error_token(cls, token: Token, message: str):
        if token.token_type == TokenType.EOF:
            cls.report(token.line, " at end", message)
        else:
            cls.report(token.line, f" at '{token.lexeme}'", message)

    @classmethod
    def runtime_error(cls, error: RunTimeError):
        print(f"{error.message}\n[line {error.token.line}]")
        cls.had_runtime_error = True

    @classmethod
    def report(cls, line: int, where: str, message: str):
        print(f"[line {line}] Error {where}: {message}")
        cls.had_error = True