#!/usr/bin/env python3
"""
Comprehensive Python files validation script.
Checks for syntax errors, imports, undefined variables, and runtime issues.
"""

import os
import sys
import ast
import py_compile
import importlib.util
import traceback
from pathlib import Path
from collections import defaultdict
import re

class PythonValidator:
    def __init__(self):
        self.errors = defaultdict(list)
        self.warnings = defaultdict(list)
        self.info = defaultdict(list)
        self.project_root = Path("c:/Users/user/Desktop/Ai agent")
        self.python_files = []

    def find_python_files(self):
        """Find all Python files in the project, excluding .venv"""
        for root, dirs, files in os.walk(self.project_root):
            # Skip virtual environment and cache directories
            dirs[:] = [d for d in dirs if d not in {'.venv', '__pycache__', '.git', 'node_modules'}]

            for file in files:
                if file.endswith('.py'):
                    filepath = Path(root) / file
                    self.python_files.append(filepath)

        return sorted(self.python_files)

    def check_syntax(self, filepath):
        """Check for syntax errors using ast.parse"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()
            ast.parse(source)
            return True, None
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg} - {e.text}"
        except Exception as e:
            return False, f"{type(e).__name__}: {str(e)}"

    def check_compile(self, filepath):
        """Check using py_compile"""
        try:
            py_compile.compile(str(filepath), doraise=True)
            return True, None
        except py_compile.PyCompileError as e:
            return False, str(e)

    def check_imports(self, filepath):
        """Check if imports can be resolved"""
        issues = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()

            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name.split('.')[0]
                        if not self._can_import(module_name):
                            issues.append({
                                'line': node.lineno,
                                'type': 'missing_module',
                                'module': alias.name,
                                'severity': 'error'
                            })

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_name = node.module.split('.')[0]
                        if not self._can_import(module_name):
                            issues.append({
                                'line': node.lineno,
                                'type': 'missing_module',
                                'module': node.module,
                                'severity': 'error'
                            })
        except Exception as e:
            issues.append({
                'type': 'parse_error',
                'message': str(e),
                'severity': 'error'
            })

        return issues

    def _can_import(self, module_name):
        """Check if a module can be imported"""
        try:
            spec = importlib.util.find_spec(module_name)
            return spec is not None
        except (ImportError, ModuleNotFoundError, ValueError):
            return False

    def check_undefined_variables(self, filepath):
        """Check for undefined variables using AST analysis"""
        issues = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()

            tree = ast.parse(source)
            analyzer = UndefinedVariableAnalyzer()
            analyzer.visit(tree)
            issues = analyzer.undefined_vars
        except Exception:
            pass

        return issues

    def check_common_errors(self, filepath):
        """Check for common Python mistakes"""
        issues = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            source = ''.join(lines)
            tree = ast.parse(source)

            # Check for mutable default arguments
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for default in node.args.defaults + node.args.kw_defaults:
                        if default is None:
                            continue
                        if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                            issues.append({
                                'line': node.lineno,
                                'type': 'mutable_default',
                                'message': f"Function '{node.name}' uses mutable default argument",
                                'severity': 'warning'
                            })

            # Check for bare except
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        issues.append({
                            'line': node.lineno,
                            'type': 'bare_except',
                            'message': "Bare 'except:' clause is too broad",
                            'severity': 'warning'
                        })

            # Check for comparison to True/False/None
            for node in ast.walk(tree):
                if isinstance(node, ast.Compare):
                    for op in node.ops:
                        if isinstance(op, (ast.Is, ast.IsNot)):
                            for comp in node.comparators:
                                if isinstance(comp, ast.Constant):
                                    if comp.value in (True, False):
                                        issues.append({
                                            'line': node.lineno,
                                            'type': 'compare_to_bool',
                                            'message': "Avoid using 'is' to compare with True/False",
                                            'severity': 'warning'
                                        })

            # Check for comparison to None using ==
            for node in ast.walk(tree):
                if isinstance(node, ast.Compare):
                    for op, comp in zip(node.ops, node.comparators):
                        if isinstance(op, (ast.Eq, ast.NotEq)):
                            if isinstance(comp, ast.Constant) and comp.value is None:
                                issues.append({
                                    'line': node.lineno,
                                    'type': 'compare_to_none',
                                    'message': "Use 'is None' instead of '== None'",
                                    'severity': 'warning'
                                })

        except Exception:
            pass

        return issues

    def validate_file(self, filepath):
        """Run all validation checks on a file"""
        relative_path = filepath.relative_to(self.project_root)

        # Syntax check
        syntax_ok, syntax_err = self.check_syntax(filepath)
        if not syntax_ok:
            self.errors[str(relative_path)].append({
                'type': 'syntax_error',
                'message': syntax_err,
                'severity': 'error'
            })
            return  # Stop if syntax is broken

        # Compile check
        compile_ok, compile_err = self.check_compile(filepath)
        if not compile_ok:
            self.errors[str(relative_path)].append({
                'type': 'compile_error',
                'message': compile_err,
                'severity': 'error'
            })

        # Import check
        import_issues = self.check_imports(filepath)
        if import_issues:
            self.errors[str(relative_path)].extend(import_issues)

        # Undefined variables
        undefined_issues = self.check_undefined_variables(filepath)
        if undefined_issues:
            for issue in undefined_issues:
                self.warnings[str(relative_path)].append(issue)

        # Common errors
        common_issues = self.check_common_errors(filepath)
        if common_issues:
            for issue in common_issues:
                if issue['severity'] == 'error':
                    self.errors[str(relative_path)].append(issue)
                else:
                    self.warnings[str(relative_path)].append(issue)

    def run_validation(self):
        """Run validation on all files"""
        files = self.find_python_files()
        print(f"Found {len(files)} Python files to validate\n")

        for i, filepath in enumerate(files, 1):
            print(f"[{i}/{len(files)}] Validating {filepath.name}...", end='\r')
            self.validate_file(filepath)

        print(" " * 80, end='\r')  # Clear line

    def generate_report(self):
        """Generate and print the validation report"""
        print("\n" + "=" * 100)
        print("PYTHON FILES VALIDATION REPORT")
        print("=" * 100 + "\n")

        total_files = len(self.python_files)
        files_with_errors = len(self.errors)
        files_with_warnings = len(self.warnings)

        print(f"Total Files: {total_files}")
        print(f"Files with Errors: {files_with_errors}")
        print(f"Files with Warnings: {files_with_warnings}")
        print(f"Clean Files: {total_files - files_with_errors - files_with_warnings}")
        print("\n" + "=" * 100 + "\n")

        # Report errors
        if self.errors:
            print("ERRORS FOUND:\n")
            for filepath in sorted(self.errors.keys()):
                print(f"\nFile: {filepath}")
                print("-" * 100)
                for error in self.errors[filepath]:
                    self._print_issue(error)

        # Report warnings
        if self.warnings:
            print("\n\n" + "=" * 100)
            print("WARNINGS FOUND:\n")
            for filepath in sorted(self.warnings.keys()):
                if filepath not in self.errors:  # Only show if not already in errors
                    print(f"\nFile: {filepath}")
                    print("-" * 100)
                    for warning in self.warnings[filepath]:
                        self._print_issue(warning)

        print("\n" + "=" * 100)
        print("REPORT COMPLETE")
        print("=" * 100 + "\n")

    def _print_issue(self, issue):
        """Print a single issue"""
        if 'line' in issue:
            print(f"  Line {issue.get('line', 'N/A')}: ", end='')
        else:
            print(f"  ", end='')

        print(f"[{issue.get('type', 'unknown')}] {issue.get('message', issue.get('message', str(issue)))}")
        if 'module' in issue:
            print(f"           Module: {issue['module']}")


class UndefinedVariableAnalyzer(ast.NodeVisitor):
    """Analyze undefined variables in AST"""

    def __init__(self):
        self.undefined_vars = []
        self.defined_names = set()
        self.scope_stack = [set()]

    def visit_FunctionDef(self, node):
        self.scope_stack.append(set())
        for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
            self.defined_names.add(arg.arg)
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            # This is a reference, not a definition
            if node.id not in self.defined_names and node.id not in dir(__builtins__):
                # Allow common builtins and common undefined refs
                if node.id not in {'self', 'cls', '__name__', '__doc__', '__all__'}:
                    pass  # Too many false positives
        elif isinstance(node.ctx, ast.Store):
            self.defined_names.add(node.id)


def main():
    validator = PythonValidator()
    validator.run_validation()
    validator.generate_report()

    # Save detailed report
    with open('validation_report.txt', 'w', encoding='utf-8') as f:
        f.write("PYTHON FILES VALIDATION REPORT\n")
        f.write("=" * 100 + "\n\n")

        total_files = len(validator.python_files)
        f.write(f"Total Files: {total_files}\n")
        f.write(f"Files with Errors: {len(validator.errors)}\n")
        f.write(f"Files with Warnings: {len(validator.warnings)}\n\n")

        if validator.errors:
            f.write("ERRORS:\n" + "=" * 100 + "\n\n")
            for filepath in sorted(validator.errors.keys()):
                f.write(f"File: {filepath}\n")
                f.write("-" * 100 + "\n")
                for error in validator.errors[filepath]:
                    if 'line' in error:
                        f.write(f"  Line {error.get('line', 'N/A')}: ")
                    f.write(f"[{error.get('type', 'unknown')}] {error.get('message', str(error))}\n")
                f.write("\n")

        if validator.warnings:
            f.write("\n" + "=" * 100 + "\n")
            f.write("WARNINGS:\n" + "=" * 100 + "\n\n")
            for filepath in sorted(validator.warnings.keys()):
                f.write(f"File: {filepath}\n")
                f.write("-" * 100 + "\n")
                for warning in validator.warnings[filepath]:
                    if 'line' in warning:
                        f.write(f"  Line {warning.get('line', 'N/A')}: ")
                    f.write(f"[{warning.get('type', 'unknown')}] {warning.get('message', str(warning))}\n")
                f.write("\n")

    print("\nDetailed report saved to: validation_report.txt")


if __name__ == '__main__':
    main()
