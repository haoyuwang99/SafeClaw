#!/usr/bin/env python3
# calculator.py - evaluates simple math expressions from the command line

import sys
import ast
import operator

# Safe operator whitelist
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}

def safe_eval(expr):
    """Evaluate a math expression safely using AST parsing."""
    try:
        tree = ast.parse(expr, mode='eval')
    except SyntaxError:
        raise ValueError(f"Invalid expression: {expr}")

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        elif isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](_eval(node.operand))
        else:
            raise ValueError(f"Unsupported operation: {ast.dump(node)}")

    return _eval(tree)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: calculator.py \"2 + 2 * 10\"")
        sys.exit(1)

    expr = ' '.join(sys.argv[1:])
    result = safe_eval(expr)
    print(f"{expr} = {result}")
