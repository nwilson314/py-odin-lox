from typing import Any

from error import Error
from token_type import Token, TokenType


keywords = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "for": TokenType.FOR,
    "fun": TokenType.FUN,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}

class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

    
    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self) -> None:
        c = self.advance()

        match c:
            case '(':
                self.add_token(TokenType.LEFT_PAREN)
            case ')':
                self.add_token(TokenType.RIGHT_PAREN)
            case '{':
                self.add_token(TokenType.LEFT_BRACE)
            case '}':
                self.add_token(TokenType.RIGHT_BRACE)
            case ',':
                self.add_token(TokenType.COMMA)
            case '.':
                self.add_token(TokenType.DOT)
            case '-':
                self.add_token(TokenType.MINUS)
            case '+':
                self.add_token(TokenType.PLUS)
            case ';':
                self.add_token(TokenType.SEMICOLON)
            case '*':
                self.add_token(TokenType.STAR)
            case '!':
                tt = TokenType.BANG if self.match('=') else TokenType.BANG
                self.add_token(tt)
            case '=':
                tt = TokenType.EQUAL if not self.match('=') else TokenType.EQUAL_EQUAL
                self.add_token(tt)
            case '>':
                tt = TokenType.GREATER if not self.match('=') else TokenType.GREATER_EQUAL
                self.add_token(tt)
            case '<':
                tt = TokenType.LESS if not self.match('=') else TokenType.LESS_EQUAL
                self.add_token(tt)
            case '/':
                if self.match('/'):
                    # A comment goes until the end of the line.
                    while self.peek() != '\n' and not self.is_at_end():
                        self.advance()
                else:
                    self.add_token(TokenType.SLASH)
            case ' ' | '\r' | '\t':
                pass
            case '\n':
                self.line += 1
            case '"':
                self.string_eval()
            case _:
                if self.is_digit(c):
                    self.number_eval()
                elif self.is_alpha(c):
                    self.identifier_eval()
                else:
                    Error.error(self.line, f"Unexpected character: {c}")

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]

    def add_token(self, token_type: TokenType, literal: Any = None) -> None:
        text = self.source[self.start:self.current] # Might be self.current+1
        self.tokens.append(Token(token_type, text, literal, self.line))

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False

        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self) -> str:
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def string_eval(self) -> None: 
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        
        if self.is_at_end():
            Error.error(self.line, "Unterminated string.")

        # The closing quote
        self.advance()

        value = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING, value)

    def number_eval(self) -> None:
        while self.is_digit(self.peek()):
            self.advance()

        if self.peek() == '.' and self.is_digit(self.peek_next()):
            # Look for a fractional part.
            self.advance()

            while self.is_digit(self.peek()):
                self.advance()

        value = float(self.source[self.start:self.current])
        self.add_token(TokenType.NUMBER, value)

    def identifier_eval(self) -> None:
        while self.is_alpha_numeric(self.peek()):
            self.advance()

        text = self.source[self.start:self.current]
        tt = keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(tt)

    def is_digit(self, c: str) -> bool:
        return c >= '0' and c <= '9'

    def is_alpha(self, c: str) -> bool:
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or c == '_'

    def is_alpha_numeric(self, c: str) -> bool:
        return self.is_digit(c) or self.is_alpha(c)
