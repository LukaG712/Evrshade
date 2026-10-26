"""
Security tests for install-gui-win.py (Windows installer).

Verifies the command injection fixes (CWE-78).
Run with: pytest tests/test_install_gui_win_security.py -v
"""

import ast
import importlib.util
import inspect
import os
import re
import sys
import unittest
from unittest import mock

# Resolve the project root (parent of the tests directory)
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_INSTALL_GUI_WIN_PATH = os.path.join(_PROJECT_ROOT, "install-gui-win.py")


def _load_install_gui_win_module():
    """Dynamically load install-gui-win.py without importing tkinter."""
    spec = importlib.util.spec_from_file_location(
        "install_gui_win", _INSTALL_GUI_WIN_PATH
    )
    mod = importlib.util.module_from_spec(spec)

    # Mock tkinter and ctypes before executing
    sys.modules["tkinter"] = mock.MagicMock()
    sys.modules["tkinter.ttk"] = mock.MagicMock()
    sys.modules["tkinter.filedialog"] = mock.MagicMock()
    sys.modules["tkinter.messagebox"] = mock.MagicMock()

    # Mock ctypes for Windows admin check
    mock_ctypes = mock.MagicMock()
    sys.modules["ctypes"] = mock_ctypes

    spec.loader.exec_module(mod)
    return mod


class TestNoShellTrue(unittest.TestCase):
    """Verify install-gui-win.py contains NO shell=True calls (CWE-78 fix)."""

    @classmethod
    def setUpClass(cls):
        with open(_INSTALL_GUI_WIN_PATH, "r", encoding="utf-8") as f:
            cls.source = f.read()

    def test_no_shell_true_in_source(self):
        """The source code must not contain 'shell=True' anywhere."""
        self.assertNotIn(
            "shell=True",
            self.source,
            "install-gui-win.py must not use shell=True — this enables command injection",
        )

    def test_run_command_uses_shell_false(self):
        """The run_command function must explicitly pass shell=False."""
        self.assertIn(
            "shell=False",
            self.source,
            "run_command must use shell=False to prevent command injection",
        )

    def test_no_fstring_in_run_command_calls(self):
        """
        No run_command() call should use an f-string that constructs shell commands
        with user-controlled values.
        """
        tree = ast.parse(self.source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                func_name = ""
                if isinstance(func, ast.Name):
                    func_name = func.id
                elif isinstance(func, ast.Attribute):
                    func_name = func.attr

                if func_name == "run_command" and node.args:
                    first_arg = node.args[0]
                    self.assertNotIsInstance(
                        first_arg,
                        ast.JoinedStr,
                        f"run_command() at line {node.lineno} uses an f-string argument — "
                        "this is a command injection risk. Use a list instead.",
                    )

    def test_no_cd_and_chains_in_source(self):
        """
        The source should not contain 'cd ... &&' shell chains.
        These were replaced with cwd= parameter.
        """
        cd_chain_pattern = re.compile(r"cd\s+['\"]?\$\{?{?self\.install_dir")
        matches = cd_chain_pattern.findall(self.source)
        self.assertEqual(
            len(matches),
            0,
            "Found 'cd' shell chains in source — use cwd= parameter instead",
        )

    def test_run_command_accepts_cwd(self):
        """run_command() must accept a cwd parameter for safe directory switching."""
        mod = _load_install_gui_win_module()
        sig = inspect.signature(mod.run_command)
        self.assertIn(
            "cwd",
            sig.parameters,
            "run_command must accept a 'cwd' parameter",
        )


class TestInstallerMethodsNoShellInjection(unittest.TestCase):
    """
    Verify that Installer class methods use list-based arguments,
    not f-strings with user-controlled values.
    """

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_install_gui_win_module()
        with open(_INSTALL_GUI_WIN_PATH, "r", encoding="utf-8") as f:
            cls.source = f.read()

    def _assert_no_fstring_arg(self, call_node, method_name):
        """Assert run_command does not use an f-string argument."""
        if not call_node.args:
            return
        first_arg = call_node.args[0]
        self.assertNotIsInstance(
            first_arg,
            ast.JoinedStr,
            f"{method_name} line {call_node.lineno}: "
            f"run_command must not use an f-string argument",
        )

    def test_clone_repo_uses_list_args(self):
        """clone_repo() must not use f-string arguments for git commands."""
        tree = ast.parse(self.source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "clone_repo":
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        func_name = ""
                        if isinstance(child.func, ast.Name):
                            func_name = child.func.id
                        elif isinstance(child.func, ast.Attribute):
                            func_name = child.func.attr
                        if func_name == "run_command":
                            self._assert_no_fstring_arg(child, "clone_repo")
                break

    def test_install_services_uses_list_args(self):
        """install_services() must not use f-string arguments."""
        tree = ast.parse(self.source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "install_services":
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        func_name = ""
                        if isinstance(child.func, ast.Name):
                            func_name = child.func.id
                        elif isinstance(child.func, ast.Attribute):
                            func_name = child.func.attr
                        if func_name == "run_command":
                            self._assert_no_fstring_arg(child, "install_services")
                break

    def test_start_services_uses_list_args(self):
        """start_services() must not use f-string arguments."""
        tree = ast.parse(self.source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "start_services":
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        func_name = ""
                        if isinstance(child.func, ast.Name):
                            func_name = child.func.id
                        elif isinstance(child.func, ast.Attribute):
                            func_name = child.func.attr
                        if func_name == "run_command":
                            self._assert_no_fstring_arg(child, "start_services")
                break


if __name__ == "__main__":
    unittest.main()
