from expr import Expr, Binary, Grouping, Unary, Literal
from token_type import Token, TokenType

from error import Error, ParseError

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Expr | None:
        try:
            return self.expression()
        except ParseError as e:
            return None

    def expression(self) -> Expr:
        """
        An expression simply expands to the equality rule

        expression -> equality
        """
        return self.equality()

    def equality(self) -> Expr:
        """
        equality -> comparison ( ( '!=' | '==' ) comparison ) *
        """
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        """
        comparison -> term ( ( '>' | '>=' | '<' | '<=' ) term ) *
        """
        expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        
        return expr

    def term(self) -> Expr:
        """
        term -> factor ( ( '-' | '+' ) factor ) *
        """
        expr = self.factor()
        
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        """
        factor -> unary ( ( '/' | '*' ) unary ) *
        """
        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr:
        """
        unary -> ( '!' | '-' ) unary
                 | primary
        """
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        
        return self.primary()

    def primary(self) -> Expr:
        """
        primary -> NUMBER | STRING | 'true' | 'false' | 'nil' | '(' expression ')'
        """
        if self.match(TokenType.FALSE): return Literal(False)
        if self.match(TokenType.TRUE): return Literal(True)
        if self.match(TokenType.NIL): return Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression.")
            return Grouping(expr)

        raise self.raise_error(self.peek(), "Expected expression.")

    def consume(self, token_type: TokenType, message: str):
        if self.check(token_type):
            return self.advance()
        raise self.raise_error(self.peek(), message)

    def match(self, *token_types: TokenType) -> bool:
        """
        Checks to see if the current token has any of the given types. If so, it consumes the token and returns True.
        Otherwise, it returns False and leaves the current token unchanged.
        """
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def check(self, token_type: TokenType) -> bool:
        """
        Return true if the current token is of the given type. Never consumes the token.
        """
        if self.is_at_end():
            return False
        return self.peek().token_type == token_type

    def advance(self) -> Token:
        """
        Consumes the current token and returns it.
        """
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().token_type == TokenType.EOF
    
    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def raise_error(self, token: Token, message: str) -> 'ParseError':
        Error.error_token(token, message)
        return ParseError(message)

    def synchronize(self) -> None:
        self.advance()

        while not self.is_at_end():
            if self.previous().token_type == TokenType.SEMICOLON:
                return
            
            match self.peek().token_type:
                case (TokenType.CLASS |
                     TokenType.FUN |
                     TokenType.VAR |
                     TokenType.FOR |
                     TokenType.IF |
                     TokenType.WHILE |
                     TokenType.PRINT |
                     TokenType.RETURN):
                     return

            self.advance()
    
