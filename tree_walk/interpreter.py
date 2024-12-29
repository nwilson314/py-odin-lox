from decimal import Decimal
from typing import Any

from error import RunTimeError, Error, ParseError
from environment import Environment
from expr import Visitor as ExprVisitor, Literal, Grouping, Expr, Unary, Binary, Variable, Assign
from stmt import Visitor as StmtVisitor, Expression, Print, Stmt, Var, Block
from token_type import TokenType, Token

class Interpreter(ExprVisitor[Any], StmtVisitor[Any]):
    def __init__(self):
        self.environment = Environment()

    def interpret(self, statements: list[Stmt]) -> None:
        try:
            for statement in statements:
                self.execute(statement)
        except RunTimeError as error:
            Error.runtime_error(error)

    def visit_literal_expr(self, expr: Literal) -> Any:
        return expr.value

    def visit_grouping_expr(self, expr: Grouping) -> Any:
        return self.evaluate(expr.expression)

    def visit_unary_expr(self, expr: Unary) -> Any:
        right = self.evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.BANG:
                return not self.is_truthy(right)
            case TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -Decimal(right)

        return None # unreachable

    def visit_binary_expr(self, expr: Binary) -> Any:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.GREATER:
                self.check_number_operands(expr.operator, left, right)
                return Decimal(left) > Decimal(right)
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return Decimal(left) >= Decimal(right)
            case TokenType.LESS:
                self.check_number_operands(expr.operator, left, right)
                return Decimal(left) < Decimal(right)
            case TokenType.LESS_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return Decimal(left) <= Decimal(right)
            case TokenType.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return Decimal(left) - Decimal(right)
            case TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)
            case TokenType.PLUS:
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                if isinstance(left, Decimal) and isinstance(right, Decimal):
                    return left + right
                raise RunTimeError(expr.operator, "Operands must be two strings or two numbers.")
            case TokenType.SLASH:
                self.check_number_operands(expr.operator, left, right)
                return Decimal(left) / Decimal(right)
            case TokenType.STAR:
                self.check_number_operands(expr.operator, left, right)
                return Decimal(left) * Decimal(right)
            
        return None # unreachable

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self.evaluate(stmt.expression)

    def visit_print_stmt(self, stmt: Print) -> None:
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visit_var_stmt(self, stmt: Var) -> None:
        value = None
        if stmt.initializer != None:
            value = self.evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)

    def visit_variable_expr(self, expr: Variable) -> Any:
        return self.environment.get(expr.name)

    def visit_assign_expr(self, expr: Assign) -> Any:
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visit_block_stmt(self, stmt: Block) -> None:
        self.execute_block(stmt.statements, Environment(self.environment))

    def evaluate(self, expr: Expr) -> Any:
        return expr.accept(self)

    def execute(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def execute_block(self, statements: list[Stmt], environment: Environment) -> None:
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def is_truthy(self, value: Any) -> bool:
        if value is None: return False
        if isinstance(value, bool): return value
        return True

    def is_equal(self, left: Any, right: Any) -> bool:
        if left is None and right is None: return True
        if left is None: return False

        return left == right

    def check_number_operand(self, operator: Token, operand: Any) -> None:
        if isinstance(operand, Decimal):
            return
        raise RunTimeError(operator, "Operand must be a number.")

    def check_number_operands(self, operator: Token, left: Any, right: Any) -> None:
        if isinstance(left, Decimal) and isinstance(right, Decimal):
            return

        raise RunTimeError(operator, "Operands must be numbers.")

    def stringify(self, object):
        if object is None:
            return "nil"
        else:
            return str(object)