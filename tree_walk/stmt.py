'''
This code is generated automatically by generate_ast.py
'''

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from token_type import Token
from expr import Expr

T = TypeVar('T')

class Stmt(ABC):
	@abstractmethod
	def accept(self, visitor: 'Visitor[T]') -> T:
		pass

class Block(Stmt):
	def __init__(self, statements: list[Stmt]):
		self.statements = statements

	def accept(self, visitor: 'Visitor[T]') -> T:
		return visitor.visit_block_stmt(self)

class Expression(Stmt):
	def __init__(self, expression: Expr):
		self.expression = expression

	def accept(self, visitor: 'Visitor[T]') -> T:
		return visitor.visit_expression_stmt(self)

class If(Stmt):
	def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Stmt):
		self.condition = condition
		self.then_branch = then_branch
		self.else_branch = else_branch

	def accept(self, visitor: 'Visitor[T]') -> T:
		return visitor.visit_if_stmt(self)

class Print(Stmt):
	def __init__(self, expression: Expr):
		self.expression = expression

	def accept(self, visitor: 'Visitor[T]') -> T:
		return visitor.visit_print_stmt(self)

class Var(Stmt):
	def __init__(self, name: Token, initializer: Expr):
		self.name = name
		self.initializer = initializer

	def accept(self, visitor: 'Visitor[T]') -> T:
		return visitor.visit_var_stmt(self)

class While(Stmt):
	def __init__(self, condition: Expr, body: Stmt):
		self.condition = condition
		self.body = body

	def accept(self, visitor: 'Visitor[T]') -> T:
		return visitor.visit_while_stmt(self)

class Visitor(Generic[T]):
	@abstractmethod
	def visit_block_stmt(self, expr: Block) -> T:
		pass

	@abstractmethod
	def visit_expression_stmt(self, expr: Expression) -> T:
		pass

	@abstractmethod
	def visit_if_stmt(self, expr: If) -> T:
		pass

	@abstractmethod
	def visit_print_stmt(self, expr: Print) -> T:
		pass

	@abstractmethod
	def visit_var_stmt(self, expr: Var) -> T:
		pass

	@abstractmethod
	def visit_while_stmt(self, expr: While) -> T:
		pass

