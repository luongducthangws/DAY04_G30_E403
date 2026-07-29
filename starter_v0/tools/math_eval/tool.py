from __future__ import annotations

import ast
import operator
from typing import Any

# Allowed operators mapping
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Allowed safe functions
ALLOWED_FUNCTIONS = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "pow": pow,
}


def _safe_eval_ast(node: ast.AST) -> Any:
    if isinstance(node, ast.Expression):
        return _safe_eval_ast(node.body)
    elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    elif isinstance(node, ast.Num):  # Python < 3.8 compatibility
        return node.n
    elif isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
        return OPERATORS[type(node.op)](_safe_eval_ast(node.operand))
    elif isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
        left = _safe_eval_ast(node.left)
        right = _safe_eval_ast(node.right)
        if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)) and right == 0:
            raise ZeroDivisionError("Division by zero is not allowed.")
        return OPERATORS[type(node.op)](left, right)
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        func_name = node.func.id
        if func_name not in ALLOWED_FUNCTIONS:
            raise ValueError(f"Function '{func_name}' is not allowed in math_eval.")
        args = [_safe_eval_ast(arg) for arg in node.args]
        return ALLOWED_FUNCTIONS[func_name](*args)
    elif isinstance(node, ast.List):
        return [_safe_eval_ast(elt) for elt in node.elts]
    elif isinstance(node, ast.Tuple):
        return tuple(_safe_eval_ast(elt) for elt in node.elts)
    else:
        raise ValueError(f"Unsupported mathematical expression element: {type(node).__name__}")


def math_eval(expression: str = "") -> dict[str, Any]:
    """Safely evaluates a mathematical expression string.

    Args:
        expression: A math expression, e.g. "(100 * 1.15) / 2" or "round(45.67, 1)".

    Returns:
        Dictionary containing expression, numeric result, formatted result, and error.
    """
    if not isinstance(expression, str) or not expression.strip():
        return {
            "expression": expression,
            "result": None,
            "formatted_result": "",
            "error": "Expression must be a non-empty string.",
        }

    clean_expr = expression.strip()
    try:
        parsed = ast.parse(clean_expr, mode="eval")
        res = _safe_eval_ast(parsed)

        # Format integer values nicely if result is float with no decimals
        if isinstance(res, float) and res.is_integer():
            formatted = str(int(res))
        elif isinstance(res, (int, float)):
            formatted = f"{res:g}"
        else:
            formatted = str(res)

        return {
            "expression": clean_expr,
            "result": res,
            "formatted_result": formatted,
            "error": None,
        }
    except ZeroDivisionError as e:
        return {
            "expression": clean_expr,
            "result": None,
            "formatted_result": "",
            "error": f"Division by zero error: {e}",
        }
    except Exception as exc:
        return {
            "expression": clean_expr,
            "result": None,
            "formatted_result": "",
            "error": f"Invalid math expression '{clean_expr}': {exc}",
        }
