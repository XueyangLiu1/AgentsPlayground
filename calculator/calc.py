"""Command-line interactive calculator with recursive descent parser."""

import math
import re


EASTER_EGG = 2.876543897


def format_num(n: float) -> str:
    """Format number: show as int if whole, else as float."""
    if math.isinf(n) or math.isnan(n):
        return str(n)
    n = round(n, 10)
    return str(int(n)) if n == int(n) else str(n)


class ParseError(Exception):
    pass


class Parser:
    """Recursive descent parser for arithmetic expressions.

    Precedence (high to low):
        1. 唔得比 (easter egg, highest)
        2. Parentheses / number literals
        3. Postfix ! (factorial)
        4. ^ (right-associative)
        5. Unary -
        6. * /
        7. + -
    """

    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    def _skip_spaces(self):
        while self.pos < len(self.text) and self.text[self.pos] == " ":
            self.pos += 1

    def _peek(self, n=1):
        return self.text[self.pos : self.pos + n]

    def _at_end(self):
        return self.pos >= len(self.text)

    def parse(self) -> float:
        result = self._expr_add_sub()
        self._skip_spaces()
        if not self._at_end():
            raise ParseError(f"unexpected character: '{self._peek()}'")
        return result

    # Level 7 (lowest): + -
    def _expr_add_sub(self) -> float:
        left = self._expr_mul_div()
        while True:
            self._skip_spaces()
            if self._at_end():
                break
            op = self._peek()
            if op in ("+", "-"):
                self.pos += 1
                right = self._expr_mul_div()
                if op == "+":
                    left = left + right
                else:
                    left = left - right
            else:
                break
        return left

    # Level 6: * /
    def _expr_mul_div(self) -> float:
        left = self._expr_unary()
        while True:
            self._skip_spaces()
            if self._at_end():
                break
            op = self._peek()
            if op in ("*", "/"):
                self.pos += 1
                right = self._expr_unary()
                if op == "*":
                    left = left * right
                else:
                    if right == 0:
                        raise ParseError("division by zero")
                    left = left / right
            else:
                break
        return left

    # Level 5: unary -
    def _expr_unary(self) -> float:
        self._skip_spaces()
        if self._peek() == "-":
            self.pos += 1
            return -self._expr_unary()
        return self._expr_power()

    # Level 4: ^ (right-associative)
    def _expr_power(self) -> float:
        base = self._expr_factorial()
        self._skip_spaces()
        if not self._at_end() and self._peek() == "^":
            self.pos += 1
            exp = self._expr_unary()  # right-associative: recurse into unary
            try:
                return base ** exp
            except OverflowError:
                raise ParseError("result too large")
        return base

    # Level 3: postfix !
    def _expr_factorial(self) -> float:
        val = self._expr_easter_egg()
        self._skip_spaces()
        while not self._at_end() and self._peek() == "!":
            self.pos += 1
            if val < 0 or val != int(val):
                raise ParseError("factorial not defined for negative or non-integer numbers")
            val = float(math.factorial(int(val)))
            self._skip_spaces()
        return val

    # Level 1 (highest): 唔得比
    def _expr_easter_egg(self) -> float:
        val = self._expr_atom()
        self._skip_spaces()
        egg = "唔得比"
        if self.text[self.pos : self.pos + len(egg)] == egg:
            self.pos += len(egg)
            self._expr_atom()  # consume right operand, discard
            return EASTER_EGG
        return val

    # Level 2: parentheses and number literals
    def _expr_atom(self) -> float:
        self._skip_spaces()
        if self._at_end():
            raise ParseError("unexpected end of expression")

        # Parenthesized expression
        if self._peek() == "(":
            self.pos += 1
            val = self._expr_add_sub()
            self._skip_spaces()
            if self._at_end() or self._peek() != ")":
                raise ParseError("missing closing parenthesis")
            self.pos += 1
            return val

        # Number
        m = re.match(r"\d+\.?\d*", self.text[self.pos :])
        if m:
            self.pos += len(m.group())
            return float(m.group())

        raise ParseError("unexpected character: '{}'".format(self._peek()))


def evaluate(expr: str) -> str:
    """Evaluate an expression string and return result as string."""
    expr = expr.strip()
    if not expr:
        return ""
    try:
        parser = Parser(expr)
        result = parser.parse()
        return format_num(result)
    except ParseError as e:
        return f"Error: {e}"
    except Exception:
        return "Error: invalid expression"


def main():
    print("Calculator (supports + - * / ^ ! () and 唔得比)")
    print("Type 'exit' or 'quit' to quit.\n")
    while True:
        try:
            line = input(">>> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.strip().lower() in ("exit", "quit"):
            break
        result = evaluate(line)
        if result:
            print(result)


if __name__ == "__main__":
    main()
