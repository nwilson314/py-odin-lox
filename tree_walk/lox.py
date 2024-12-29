import sys

from ast_printer import AstPrinter
from error import Error
from parser import Parser
from scanner import Scanner
from interpreter import Interpreter

class Lox:
    def __init__(self):
        self.interpreter = Interpreter()

    def run_file(self, path: str):
        with open(path, "r") as f:
            file = f.read()
        self.run(file)

        if Error.had_error:
            sys.exit(65)
        if Error.had_runtime_error:
            sys.exit(70)

    def run_prompt(self):
        while True:
            try:
                line = input("> ")
            except:
                break
            try:
                self.run(line)
            except Exception as e:
                print(e)
            Error.had_error = False

    def run(self, source: str):
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens)

        statements = parser.parse()

        if Error.had_error:
            return

        # print(AstPrinter().print(expression))
        self.interpreter.interpret(statements)

if __name__ == "__main__":
    lox = Lox()
    args = sys.argv[1:]
    
    if len(args) > 1:
        print("Usage: python3 lox.py [script]")
        sys.exit(64)
    elif len(args) == 1:
        print(f"Running file {args[0]}")
        lox.run_file(args[0])
    else:
        print("Running prompt")
        lox.run_prompt()