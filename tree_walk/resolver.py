from enum import Enum

from error import Error
from expr import Grouping, Visitor as ExprVisitor, Expr, Variable, Assign, Binary, Call, Literal, Unary, Logical, Get, Set, This, Super
from stmt import Visitor as StmtVisitor, Block, Stmt, Var, Function, Expression, If, Print, Return, While, Class
from token_type import Token
from interpreter import Interpreter


class FunctionType(str, Enum):
    NONE = "none"
    FUNCTION = "function"
    INITIALIZER = "initializer"
    METHOD = "method"


class ClassType(str, Enum):
    NONE = "none"
    CLASS = "class"
    SUBCLASS = "subclass"


class Resolver(ExprVisitor, StmtVisitor):
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.scopes: list[dict[str, bool]] = [] # Stack
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE

    def visit_block_stmt(self, stmt: Block) -> None:
        self.begin_scope()
        self.resolve_statements(stmt.statements)
        self.end_scope()

    def visit_class_stmt(self, stmt: Class) -> None:
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS

        self.declare(stmt.name)
        self.define(stmt.name)

        if stmt.superclass is not None:
            if stmt.name.lexeme == stmt.superclass.name.lexeme:
                Error.error(stmt.superclass.name, "A class can't inherit from itself.")

            self.current_class = ClassType.SUBCLASS
            self.resolve(stmt.superclass)

        if stmt.superclass is not None:
            self.begin_scope()
            self.scopes[-1]["super"] = True

        self.begin_scope()
        self.scopes[-1]["this"] = True

        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            self.resolve_function(method, declaration)

        self.end_scope()
        if stmt.superclass is not None:
            self.end_scope()
        self.current_class = enclosing_class
        
    def visit_expression_stmt(self, stmt: Expression) -> None:
        self.resolve(stmt.expression)

    def visit_var_stmt(self, stmt: Var) -> None:
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)

    def visit_variable_expr(self, expr: Variable) -> None:
        if self.scopes and self.scopes[-1].get(expr.name.lexeme, None) is False:
            # print(self.scopes[-1])
            Error.error(expr.name, "Can't read local variable in its own initializer.")
        
        self.resolve_local(expr, expr.name)

    def visit_assign_expr(self, expr: Assign) -> None:
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_function_stmt(self, stmt: Function) -> None:
        self.declare(stmt.name)
        self.define(stmt.name)

        self.resolve_function(stmt, FunctionType.FUNCTION)

    def visit_if_stmt(self, stmt: If) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print) -> None:
        self.resolve(stmt.expression)

    def visit_return_stmt(self, stmt: Return) -> None:
        if self.current_function == FunctionType.NONE:
            Error.error(stmt.keyword, "Can't return from top-level code.")
        if stmt.value is not None:
            if self.current_function == FunctionType.INITIALIZER:
                Error.error(stmt.keyword, "Can't return a value from an initializer.")
            self.resolve(stmt.value)

    def visit_while_stmt(self, stmt: While) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    def visit_binary_expr(self, expr: Binary) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_call_expr(self, expr: Call) -> None:
        self.resolve(expr.callee)

        for argument in expr.arguments:
            self.resolve(argument)

    def visit_get_expr(self, expr: Get) -> None:
        self.resolve(expr.object)

    def visit_grouping_expr(self, expr: Grouping) -> None:
        self.resolve(expr.expression)

    def visit_literal_expr(self, expr: Literal) -> None:
        pass

    def visit_logical_expr(self, expr: Logical) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_set_expr(self, expr: Set) -> None:
        self.resolve(expr.value)
        self.resolve(expr.object)

    def visit_super_expr(self, expr: Super) -> None:
        if self.current_class == ClassType.NONE:
            Error.error(expr.keyword, "Can't use 'super' outside of a class.")
        elif self.current_class != ClassType.SUBCLASS:
            Error.error(expr.keyword, "Can't use 'super' in a class with no superclass.")

        self.resolve_local(expr, expr.keyword)

    def visit_this_expr(self, expr: This) -> None:
        if self.current_class == ClassType.NONE:
            Error.error(expr.keyword, "Can't use 'this' outside of a class.")
            return

        self.resolve_local(expr, expr.keyword)

    def visit_unary_expr(self, expr: Unary) -> None:
        self.resolve(expr.right)

    def resolve_statements(self, statements: list[Stmt]) -> None:
        for statement in statements: 
            self.resolve(statement)

    def resolve(self, stmt: Stmt | Expr) -> None:
        stmt.accept(self)

    def resolve_local(self, expr: Expr, name: Token) -> None:
        for i in range(len(self.scopes) - 1, -1, -1):
            if self.scopes[i].get(name.lexeme, False):
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return

    def resolve_function(self, function: Function, function_type: FunctionType) -> None:
        enclosing_function = self.current_function
        self.current_function = function_type
        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve_statements(function.body)
        self.end_scope()
        self.current_function = enclosing_function

    def declare(self, name: Token) -> None:
        if not self.scopes:
            return
        scope = self.scopes[-1]

        if scope.get(name.lexeme, False):
            Error.error(name, "Already a variable with this name in this scope.")
        scope[name.lexeme] = False

    def define(self, name: Token) -> None:
        if not self.scopes:
            return
        scope = self.scopes[-1]
        scope[name.lexeme] = True

    def begin_scope(self) -> None:
        self.scopes.append({})

    def end_scope(self) -> None:
        self.scopes.pop()