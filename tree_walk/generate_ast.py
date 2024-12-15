from io import TextIOWrapper
import sys

class GenerateAST:
    def __init__(self):
        pass

    def generate_ast(self, output_dir: str):
        self.define_ast(output_dir, "Expr", [
            "Binary: Expr left, Token operator, Expr right",
            "Grouping: Expr expression",
            "Literal: Any value",
            "Unary: Token operator, Expr right",
        ])

    def define_ast(self, output_dir: str, base_name: str, types: list[str]):
        path = f"{output_dir}/{base_name.lower()}.py"
        with open(path, "w") as f:
            # Imports
            f.write("from abc import ABC, abstractmethod\nfrom typing import Any, Generic, TypeVar\n\n")
            f.write("from token_type import Token\n\n")
            f.write("T = TypeVar('T')\n\n")
            # Abstract base class
            f.write(f"class {base_name}(ABC):\n")
            f.write("\t@abstractmethod\n\tdef accept(self, visitor: 'Visitor[T]') -> T:\n\t\tpass\n\n")
            
            f.write("TExpr = TypeVar('TExpr', bound=Expr)\n\n")

            # The AST classes
            for type in types:
                split_type = type.split(":")
                class_name = split_type[0].strip()
                fields = split_type[1].strip()
                self.define_type(f, base_name, class_name, fields)

            # The Visitor type
            self.define_visitor(f, base_name, types)

    def define_type(self, f: TextIOWrapper, base_name: str, class_name: str, fields: str):
        f.write(f"class {class_name}({base_name}):\n")

        # Constructor
        field_split = fields.split(",")
        parsed_fields = [f"{field.strip().split(" ")[1].strip()}: {field.strip().split(" ")[0].strip()}" for field in field_split]
        print(field_split)
        print(parsed_fields)
        fields = ", ".join(parsed_fields)
        f.write(f"\tdef __init__(self, {fields}):\n")

        # Store fields
        for field in parsed_fields:
            f.write(f"\t\tself.{field.split(':')[0].strip()} = {field.split(':')[0].strip()}\n")

        f.write("\n")

        # Accept method
        f.write(f"\tdef accept(self, visitor: 'Visitor[T]') -> T:\n")
        f.write(f"\t\treturn visitor.visit_{class_name.lower()}_expr(self)\n\n")

    def define_visitor(self, f: TextIOWrapper, base_name: str, types: list[str]):
        class_names = ", ".join([type.split(":")[0].strip() for type in types])
        f.write("class Visitor(Generic[T]):\n")
        for type in types:
            split_type = type.split(":")
            class_name = split_type[0].strip()
            f.write(f"\t@abstractmethod\n\tdef visit_{class_name.lower()}_expr(self, expr: {class_name}) -> T:\n\t\tpass\n\n")

if __name__ == "__main__":
    args = sys.argv[1:]
    ast = GenerateAST()

    if len(args) != 1:
        print("Usage: python3 generate_ast.py [output directory]")
        sys.exit(64)
    
    output_dir = args[0]

    ast.generate_ast(output_dir)