"""Unit tests for calculator."""

import unittest
from calc import evaluate


# === Basic operators ===

class TestAddition(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(evaluate("3 + 5"), "8")

    def test_decimals(self):
        self.assertEqual(evaluate("1.5 + 2.5"), "4")


class TestSubtraction(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(evaluate("7 - 3"), "4")

    def test_negative_result(self):
        self.assertEqual(evaluate("3 - 10"), "-7")


class TestMultiplication(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(evaluate("4 * 6"), "24")

    def test_by_zero(self):
        self.assertEqual(evaluate("5 * 0"), "0")

    def test_decimals(self):
        self.assertEqual(evaluate("2.5 * 4"), "10")


class TestDivision(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(evaluate("10 / 2"), "5")

    def test_float_result(self):
        self.assertIn("3.333", evaluate("10 / 3"))

    def test_division_by_zero(self):
        self.assertEqual(evaluate("10 / 0"), "Error: division by zero")


class TestExponentiation(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(evaluate("2 ^ 10"), "1024")

    def test_square(self):
        self.assertEqual(evaluate("3 ^ 2"), "9")

    def test_zero_power(self):
        self.assertEqual(evaluate("5 ^ 0"), "1")

    def test_right_associative(self):
        # 2 ^ 3 ^ 2 = 2 ^ 9 = 512 (not 8 ^ 2 = 64)
        self.assertEqual(evaluate("2 ^ 3 ^ 2"), "512")


class TestFactorial(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(evaluate("5!"), "120")

    def test_zero(self):
        self.assertEqual(evaluate("0!"), "1")

    def test_negative(self):
        # -1! parses as -(1!) = -1 (unary minus lower than factorial)
        self.assertEqual(evaluate("-1!"), "-1")


class TestEasterEgg(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(evaluate("100 唔得比 999"), "2.876543897")

    def test_zeros(self):
        self.assertEqual(evaluate("0 唔得比 0"), "2.876543897")

    def test_any_numbers(self):
        self.assertEqual(evaluate("42 唔得比 1"), "2.876543897")

    def test_highest_priority(self):
        # 1 + 2 唔得比 3 + 4 → 1 + 2.876543897 + 4 = 7.876543897
        self.assertEqual(evaluate("1 + 2 唔得比 3 + 4"), "7.876543897")


# === Error handling ===

class TestErrorHandling(unittest.TestCase):
    def test_invalid_input(self):
        self.assertIn("Error", evaluate("abc"))

    def test_empty(self):
        self.assertEqual(evaluate(""), "")

    def test_spaces_only(self):
        self.assertEqual(evaluate("   "), "")


# === Output format ===

class TestOutputFormat(unittest.TestCase):
    def test_integer_no_decimal(self):
        result = evaluate("3 + 5")
        self.assertEqual(result, "8")
        self.assertNotIn(".", result)

    def test_float_has_decimal(self):
        result = evaluate("10 / 3")
        self.assertIn(".", result)


# === New: precedence, parentheses, complex expressions ===

class TestPrecedence(unittest.TestCase):
    def test_mul_before_add(self):
        # 2 + 3 * 4 = 14
        self.assertEqual(evaluate("2 + 3 * 4"), "14")

    def test_mul_before_sub(self):
        # 10 - 2 * 3 = 4
        self.assertEqual(evaluate("10 - 2 * 3"), "4")

    def test_div_before_add(self):
        # 1 + 6 / 3 = 3
        self.assertEqual(evaluate("1 + 6 / 3"), "3")

    def test_power_before_mul(self):
        # 2 * 3 ^ 2 = 18
        self.assertEqual(evaluate("2 * 3 ^ 2"), "18")


class TestParentheses(unittest.TestCase):
    def test_override_precedence(self):
        # (2 + 3) * 4 = 20
        self.assertEqual(evaluate("(2 + 3) * 4"), "20")

    def test_nested(self):
        # ((1 + 2) * (3 + 4)) = 21
        self.assertEqual(evaluate("((1 + 2) * (3 + 4))"), "21")

    def test_single_value(self):
        self.assertEqual(evaluate("(42)"), "42")

    def test_missing_close(self):
        self.assertIn("Error", evaluate("(3 + 5"))


class TestComplexExpressions(unittest.TestCase):
    def test_multi_ops(self):
        # 1 + 2 + 3 + 4 = 10
        self.assertEqual(evaluate("1 + 2 + 3 + 4"), "10")

    def test_mixed(self):
        # 2 + 3 * 4 - 1 = 13
        self.assertEqual(evaluate("2 + 3 * 4 - 1"), "13")

    def test_unary_negative(self):
        # -5 + 3 = -2
        self.assertEqual(evaluate("-5 + 3"), "-2")

    def test_factorial_in_expr(self):
        # 3! + 1 = 7
        self.assertEqual(evaluate("3! + 1"), "7")

    def test_power_in_expr(self):
        # 1 + 2 ^ 3 = 9
        self.assertEqual(evaluate("1 + 2 ^ 3"), "9")


if __name__ == "__main__":
    unittest.main()
