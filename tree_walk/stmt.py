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

class Visitor(Generic[T]):
	@abstractmethod
	def visit_block_stmt(self, expr: Block) -> T:
		pass

	@abstractmethod
	def visit_expression_stmt(self, expr: Expression) -> T:
		pass

	@abstractmethod
	def visit_print_stmt(self, expr: Print) -> T:
		pass

	@abstractmethod
	def visit_var_stmt(self, expr: Var) -> T:
		pass

