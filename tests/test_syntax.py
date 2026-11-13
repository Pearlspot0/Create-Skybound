"""Syntax and AST compliance tests enforcing Python 3.4 / MicroPython constraints:
- Zero f-strings (JoinedStr)
- Zero regular expressions (re module import or usage)
- Pure standard library / hardware mock compatibility
"""

import ast
import os
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MOCK_FILES = [
    os.path.join(BASE_DIR, "ti_system.py"),
    os.path.join(BASE_DIR, "ti_draw.py"),
    os.path.join(BASE_DIR, "ti_plotlib.py"),
    os.path.join(BASE_DIR, "ti_hub.py"),
]
FLOWCE_FILE = os.path.join(BASE_DIR, "flowce.py")


class ASTComplianceVisitor(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.violations = []

    def visit_JoinedStr(self, node):
        self.violations.append(
            "{}: Line {}: f-string (JoinedStr) detected. Disallowed under Python 3.4 specs.".format(
                self.filename, getattr(node, "lineno", "?")
            )
        )
        self.generic_visit(node)

    def visit_FormattedValue(self, node):
        self.violations.append(
            "{}: Line {}: FormattedValue detected. Disallowed under Python 3.4 specs.".format(
                self.filename, getattr(node, "lineno", "?")
            )
        )
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name == "re" or alias.name.startswith("re."):
                self.violations.append(
                    "{}: Line {}: 'import re' detected. Disallowed under zero-re constraint.".format(
                        self.filename, getattr(node, "lineno", "?")
                    )
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module == "re" or (node.module and node.module.startswith("re.")):
            self.violations.append(
                "{}: Line {}: 'from re import ...' detected. Disallowed under zero-re constraint.".format(
                    self.filename, getattr(node, "lineno", "?")
                )
            )
        self.generic_visit(node)

    # Python > 3.4 syntax features
    def visit_NamedExpr(self, node):
        self.violations.append(
            "{}: Line {}: Walrus operator ':=' detected. Disallowed under Python 3.4.".format(
                self.filename, getattr(node, "lineno", "?")
            )
        )
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.violations.append(
            "{}: Line {}: 'async def' detected. Disallowed under Python 3.4.".format(
                self.filename, getattr(node, "lineno", "?")
            )
        )
        self.generic_visit(node)

    def visit_Await(self, node):
        self.violations.append(
            "{}: Line {}: 'await' detected. Disallowed under Python 3.4.".format(
                self.filename, getattr(node, "lineno", "?")
            )
        )
        self.generic_visit(node)


def check_file_ast(filepath):
    """Parse a python file and return AST violations."""
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source, filename=filepath)
    visitor = ASTComplianceVisitor(filepath)
    visitor.visit(tree)
    return visitor.violations


class TestSyntaxASTCompliance(unittest.TestCase):
    """Tier 1 & Tier 2: Syntax & AST Compliance Tests."""

    def test_mock_ti_system_ast(self):
        """F2 Tier 1: Validate ti_system.py has zero f-strings, zero re, and Python 3.4 compliance."""
        path = os.path.join(BASE_DIR, "ti_system.py")
        self.assertTrue(os.path.exists(path), "ti_system.py must exist")
        violations = check_file_ast(path)
        self.assertEqual(violations, [], "Violations found in ti_system.py: {}".format(violations))

    def test_mock_ti_draw_ast(self):
        """F2 Tier 1: Validate ti_draw.py has zero f-strings, zero re, and Python 3.4 compliance."""
        path = os.path.join(BASE_DIR, "ti_draw.py")
        self.assertTrue(os.path.exists(path), "ti_draw.py must exist")
        violations = check_file_ast(path)
        self.assertEqual(violations, [], "Violations found in ti_draw.py: {}".format(violations))

    def test_mock_ti_plotlib_ast(self):
        """F2 Tier 1: Validate ti_plotlib.py has zero f-strings, zero re, and Python 3.4 compliance."""
        path = os.path.join(BASE_DIR, "ti_plotlib.py")
        self.assertTrue(os.path.exists(path), "ti_plotlib.py must exist")
        violations = check_file_ast(path)
        self.assertEqual(violations, [], "Violations found in ti_plotlib.py: {}".format(violations))

    def test_mock_ti_hub_ast(self):
        """F2 Tier 1: Validate ti_hub.py has zero f-strings, zero re, and Python 3.4 compliance."""
        path = os.path.join(BASE_DIR, "ti_hub.py")
        self.assertTrue(os.path.exists(path), "ti_hub.py must exist")
        violations = check_file_ast(path)
        self.assertEqual(violations, [], "Violations found in ti_hub.py: {}".format(violations))

    def test_flowce_exists_and_ast_compliant(self):
        """F2 Tier 1: Validate flowce.py exists and complies with zero f-strings, zero re, and Python 3.4."""
        self.assertTrue(os.path.exists(FLOWCE_FILE), "flowce.py must exist in root workspace")
        violations = check_file_ast(FLOWCE_FILE)
        self.assertEqual(violations, [], "Violations in flowce.py: {}".format("\n".join(violations)))

    def test_ast_visitor_detects_fstring(self):
        """F2 Tier 2: Boundary test - ensure visitor catches f-string violation."""
        dummy_code = "x = 42\ns = f'x is {x}'\n"
        tree = ast.parse(dummy_code)
        visitor = ASTComplianceVisitor("<dummy_fstring>")
        visitor.visit(tree)
        self.assertTrue(any("f-string" in v for v in visitor.violations))

    def test_ast_visitor_detects_re_import(self):
        """F2 Tier 2: Boundary test - ensure visitor catches 'import re'."""
        dummy_code = "import re\nre.match(r'.*', 'abc')\n"
        tree = ast.parse(dummy_code)
        visitor = ASTComplianceVisitor("<dummy_re>")
        visitor.visit(tree)
        self.assertTrue(any("import re" in v for v in visitor.violations))

    def test_ast_visitor_detects_from_re_import(self):
        """F2 Tier 2: Boundary test - ensure visitor catches 'from re import ...'."""
        dummy_code = "from re import compile, match\n"
        tree = ast.parse(dummy_code)
        visitor = ASTComplianceVisitor("<dummy_from_re>")
        visitor.visit(tree)
        self.assertTrue(any("from re import" in v for v in visitor.violations))

    def test_ast_visitor_detects_formatted_value(self):
        """F2 Tier 2: Boundary test - ensure visitor catches FormattedValue."""
        node = ast.FormattedValue(value=ast.Constant(value=10), conversion=-1, format_spec=None)
        visitor = ASTComplianceVisitor("<dummy_fv>")
        visitor.visit_FormattedValue(node)
        self.assertTrue(any("FormattedValue" in v for v in visitor.violations))

    def test_ast_visitor_detects_async_await(self):
        """F2 Tier 2: Boundary test - ensure visitor catches async/await syntax."""
        dummy_code = "async def foo():\n    await bar()\n"
        tree = ast.parse(dummy_code)
        visitor = ASTComplianceVisitor("<dummy_async>")
        visitor.visit(tree)
        self.assertTrue(any("async def" in v for v in visitor.violations))
        self.assertTrue(any("await" in v for v in visitor.violations))

    def test_mock_files_have_no_re_import_text(self):
        """F2 Tier 2: Text scan - confirm mocks do not contain 'import re' string."""
        for path in MOCK_FILES:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertNotIn("import re", content, "{} contains 'import re'".format(os.path.basename(path)))
            self.assertNotIn("from re", content, "{} contains 'from re'".format(os.path.basename(path)))

    def test_no_external_dependencies_in_flowce(self):
        """F2 Tier 2: Boundary test - ensure flowce.py does not import third-party packages (e.g. sympy, numpy)."""
        if not os.path.exists(FLOWCE_FILE):
            self.skipTest("flowce.py does not exist yet")
        with open(FLOWCE_FILE, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=FLOWCE_FILE)
        disallowed = {"sympy", "numpy", "scipy", "matplotlib", "pandas", "torch", "re"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_pkg = alias.name.split(".")[0]
                    self.assertNotIn(top_pkg, disallowed, "External or disallowed package imported: {}".format(top_pkg))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    top_pkg = node.module.split(".")[0]
                    self.assertNotIn(top_pkg, disallowed, "External or disallowed package imported: {}".format(top_pkg))


if __name__ == "__main__":
    unittest.main()
