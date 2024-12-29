'''
This code is generated automatically by generate_ast.py
'''

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from token_type import Token

T = TypeVar('T')

class Expr(ABC):
	@abstractmethod
	def accept(self, visitor: 'Visitor[T]') -> T:
		pass

class Assign(Expr):
	def __init__(self, name: Token, value: Expr):
		self.name = name
		self.value = value

	def accept(self, visitor: 'Visitor[T]') -> T:
		return visitor.visit_assign_expr(self)

class Binary(Expr):
	def __init__(self, left: Expr, operator: Token, right: Expr):
		self.left = left
		self.operator = operator
		self.right = right

	def accept(self, visitor: 'Visitor[T]') -> T:
		return visitor.visit_binary_expr(self)

class Grouping(Expr):
	def __init__(self, expression: Expr):
		self.expression = expression

	def accept(self, visitor: 'Visitor[T]') -> T:
		return visitor.visit_grouping_expr(self)

class Literal(Expr):
	def __init__(self, value: Any):
		self.value = value

	def accept(self, visitor: 'Visitor[T]') -> T:
		return visitor.visit_literal_expr(self)

class Unary(Expr):
	def __init__(self, operator: Token, right: Expr):
		self.operator = operator
		self.right = right

	def accept(self, visitor: 'Visitor[T]') -> T:
		return visitor.visit_unary_expr(self)

class Variable(Expr):
	def __init__(self, name: Token):
		self.name = name

	def accept(self, visitor: 'Visitor[T]') -> T:
		return visitor.visit_variable_expr(self)

class Visitor(Generic[T]):
	@abstractmethod
	def visit_assign_expr(self, expr: Assign) -> T:
		pass

	@abstractmethod
	def visit_binary_expr(self, expr: Binary) -> T:
		pass

	@abstractmethod
	def visit_grouping_expr(self, expr: Grouping) -> T:
		pass

	@abstractmethod
	def visit_literal_expr(self, expr: Literal) -> T:
		pass

	@abstractmethod
	def visit_unary_expr(self, expr: Unary) -> T:
		pass

	@abstractmethod
	def visit_variable_expr(self, expr: Variable) -> T:
		pass

