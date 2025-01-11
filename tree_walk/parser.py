from expr import Expr, Binary, Grouping, Unary, Literal, Variable, Assign, Logical, Call, Get, Set, This
from stmt import Stmt, Print, Expression, Var, Block, If, While, Function, Return, Class
from token_type import Token, TokenType

from error import Error, ParseError

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> list[Stmt]:
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements

    def expression(self) -> Expr:
        """
        An expression simply expands to the equality rule

        expression -> assignment ;
        """
        return self.assignment()

    def declaration(self) -> Stmt | None:
        try:
            if self.match(TokenType.CLASS):
                return self.class_declaration()
            if self.match(TokenType.FUN):
                return self.fun_declaration('function')
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError as error:
            self.synchronize()
            return None

    def statement(self) -> Stmt:
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.LEFT_BRACE):
            return Block(self.block())
        return self.expression_statement()

    def for_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'.")

        initializer = None
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after loop condition.")

        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after for clauses.")

        body = self.statement()

        if increment is not None:
            body = Block([body, Expression(increment)])

        if condition is None:
            condition = Literal(True)

        body = While(condition, body)

        if initializer is not None:
            body = Block([initializer, body])

        return body

    def if_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after if condition.")

        then_branch = self.statement()
        else_branch = None

        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return If(condition, then_branch, else_branch)

    def print_statement(self) -> Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after value.")
        return Print(value)

    def return_statement(self) -> Stmt:
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after return value.")
        return Return(keyword, value)
    
    def expression_statement(self) -> Stmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression.")
        return Expression(expr)

    def while_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after while condition.")

        body = self.statement()

        return While(condition, body)

    def block(self) -> list[Stmt]:
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after block.")
        return statements

    def assignment(self) -> Expr:
        expr = self.logical_or()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            elif isinstance(expr, Get):
                return Set(expr.object, expr.name, value)
            self.raise_error(equals, "Invalid assignment target.")

        return expr

    def logical_or(self) -> Expr:
        expr = self.logical_and()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logical_and()
            expr = Logical(expr, operator, right)
        return expr

    def logical_and(self) -> Expr:
        expr = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
        return expr

    def class_declaration(self) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expected class name.")
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after class name.")

        methods = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.fun_declaration('method'))

        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after class body.")
        return Class(name, methods)

    def fun_declaration(self, kind: str) -> Function:
        name = self.consume(TokenType.IDENTIFIER, f"Expected {kind} name.")
        self.consume(TokenType.LEFT_PAREN, f"Expected '(' after {kind} name.")
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name."))
            while self.match(TokenType.COMMA):
                if len(parameters) >= 255:
                    self.raise_error(self.peek(), "Can't have more than 255 parameters.")
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name."))
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters.")

        self.consume(TokenType.LEFT_BRACE, f"Expected '{{' after {kind} body.")
        body = self.block()
        return Function(name, parameters, body)

    def var_declaration(self) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name.")
        initializer = None

        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration.")
        return Var(name, initializer)

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
        
        return self.call()

    def call(self) -> Expr:
        expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)

            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "Expected property name after '.'.")
                expr = Get(expr, name)
            else:
                break
        return expr

    def finish_call(self, callee: Expr) -> Expr:
        arguments = []

        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                if len(arguments) >= 255:
                    self.raise_error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())
        
        paren = self.consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments.")
        return Call(callee, paren, arguments)

    def primary(self) -> Expr:
        """
        primary -> NUMBER | STRING | 'true' | 'false' | 'nil' | '(' expression ')'
        """
        if self.match(TokenType.FALSE): return Literal(False)
        if self.match(TokenType.TRUE): return Literal(True)
        if self.match(TokenType.NIL): return Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.THIS):
            return This(self.previous())
        
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())

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
    
