from expr import Binary, Grouping, Literal, Unary, Expr, Visitor
from token_type import Token, TokenType

class AstPrinter(Visitor[str]):
    def __init__(self):
        pass

    def print(self, expr: Expr) -> str:
        return expr.accept(self)

    def visit_binary_expr(self, expr: Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: Literal) -> str:
        return str(expr.value)

    def visit_unary_expr(self, expr: Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name: str, *expressions: Expr) -> str:
        return f"({name} {' '.join(expr.accept(self) for expr in expressions)})"

    
if __name__ == "__main__":
    expression = Binary(
        left=Unary(
            operator=Token(
                token_type=TokenType.MINUS,
                lexeme="-",
                literal=None,
                line=1
            ),
            right=Literal(value=123)
        ),
        operator=Token(
            token_type=TokenType.STAR,
            lexeme="*",
            literal=None,
            line=1
        ),
        right=Grouping(
            expression=Literal(value=45.67)
        )
    )

    printer = AstPrinter()
    print(printer.print(expression))