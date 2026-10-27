"""
Security tests for install-gui.py (Linux installer).

Verifies the command injection fixes (CWE-78) and SUDO_USER validation (CWE-128).
Run with: pytest tests/test_install_gui_security.py -v
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
_INSTALL_GUI_PATH = os.path.join(_PROJECT_ROOT, "install-gui.py")


def _load_install_gui_module():
    """Dynamically load install-gui.py without importing tkinter (which may be missing)."""
    spec = importlib.util.spec_from_file_location("install_gui", _INSTALL_GUI_PATH)
    mod = importlib.util.module_from_spec(spec)

    # Mock tkinter before executing the module
    sys.modules["tkinter"] = mock.MagicMock()
    sys.modules["tkinter.ttk"] = mock.MagicMock()
    sys.modules["tkinter.filedialog"] = mock.MagicMock()
    sys.modules["tkinter.messagebox"] = mock.MagicMock()

    # Mock pwd module (Linux-only) for cross-platform testing
    if "pwd" not in sys.modules:
        sys.modules["pwd"] = mock.MagicMock()

    spec.loader.exec_module(mod)
    return mod


class TestNoShellTrue(unittest.TestCase):
    """Verify install-gui.py contains NO shell=True calls (CWE-78 fix)."""

    @classmethod
    def setUpClass(cls):
        with open(_INSTALL_GUI_PATH, "r", encoding="utf-8") as f:
            cls.source = f.read()

    def test_no_shell_true_in_source(self):
        """The source code must not contain 'shell=True' anywhere."""
        self.assertNotIn(
            "shell=True",
            self.source,
            "install-gui.py must not use shell=True — this enables command injection",
        )

    def test_run_command_uses_shell_false(self):
        """The run_command function must explicitly pass shell=False."""
        self.assertIn(
            "shell=False",
            self.source,
            "run_command must use shell=False to prevent command injection",
        )

    def test_no_fstring_in_user_input_methods(self):
        """
        Methods that handle user-controlled input must not use f-strings
        in run_command() calls. This covers the critical CWE-78 attack surface.

        Checks: clone_repo, install_services, setup_docker_group, create_env,
        start_services, create_desktop_launcher.
        """
        # Methods that handle user-controlled values (install dir, username, profile)
        user_input_methods = {
            "clone_repo",
            "install_services",
            "setup_docker_group",
            "create_env",
            "start_services",
            "create_desktop_launcher",
        }

        tree = ast.parse(self.source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in user_input_methods:
                # Check all run_command calls in this method
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        func_name = ""
                        if isinstance(child.func, ast.Name):
                            func_name = child.func.id
                        elif isinstance(child.func, ast.Attribute):
                            func_name = child.func.attr

                        if func_name == "run_command" and child.args:
                            first_arg = child.args[0]
                            self.assertNotIsInstance(
                                first_arg,
                                ast.JoinedStr,
                                f"{node.name}() at line {child.lineno} uses an f-string "
                                f"in run_command() — this is a command injection risk. "
                                f"Use a list instead.",
                            )

    def test_no_cd_and_chains_in_source(self):
        """
        The source should not contain 'cd ... &&' shell chains.
        These were replaced with cwd= parameter.
        """
        # Look for patterns like: f"cd '{self.install_dir}' && git ..."
        cd_chain_pattern = re.compile(r"cd\s+['\"]?\$\{?{?self\.install_dir")
        matches = cd_chain_pattern.findall(self.source)
        self.assertEqual(
            len(matches),
            0,
            "Found 'cd' shell chains in source — use cwd= parameter instead",
        )

    def test_run_command_accepts_cwd(self):
        """run_command() must accept a cwd parameter for safe directory switching."""
        mod = _load_install_gui_module()
        sig = inspect.signature(mod.run_command)
        self.assertIn(
            "cwd",
            sig.parameters,
            "run_command must accept a 'cwd' parameter",
        )


class TestRunCommandListArgs(unittest.TestCase):
    """Verify run_command works correctly with list arguments."""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_install_gui_module()

    def test_run_command_with_list(self):
        """run_command should accept a list of arguments."""
        # Use 'python -c' which works cross-platform
        rc, out, _err = self.mod.run_command(["python", "-c", "print('hello')"])
        self.assertEqual(rc, 0)
        self.assertIn("hello", out)

    def test_run_command_with_string(self):
        """run_command should accept a string and split it with shlex."""
        rc, out, _err = self.mod.run_command('python -c "print(1+1)"')
        self.assertEqual(rc, 0)
        self.assertIn("2", out)

    def test_run_command_with_cwd(self):
        """run_command should support cwd parameter."""
        rc, out, _err = self.mod.run_command(
            ["python", "-c", "import os; print(os.getcwd())"],
            cwd=_PROJECT_ROOT,
        )
        self.assertEqual(rc, 0)
        # The cwd should be the project root directory
        self.assertIn(os.path.basename(_PROJECT_ROOT), out)

    def test_run_command_no_shell_expansion(self):
        """
        Verify that shell metacharacters are NOT expanded.
        With shell=False, '*' is passed literally, not expanded by the shell.
        """
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file in the temp dir
            test_file = os.path.join(tmpdir, "testfile.txt")
            with open(test_file, "w") as f:
                f.write("test")

            # With shell=False, python -c "import sys; print(sys.argv[1])" "*"
            # should print literal '*'
            rc, out, _err = self.mod.run_command(
                ["python", "-c", "import sys; print(sys.argv[1])", "*"],
                cwd=tmpdir,
            )
            self.assertEqual(rc, 0)
            self.assertEqual(
                out.strip(),
                "*",
                "Shell glob expansion occurred — shell=False is not working",
            )


class TestUsernameValidation(unittest.TestCase):
    """
    Verify SUDO_USER validation against /etc/passwd (CWE-128 fix).

    These tests mock pwd.getpwnam() since we may run on Windows.
    """

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_install_gui_module()

    def _mock_getpwnam(self, valid_users):
        """Create a mock for pwd.getpwnam that returns valid users."""

        def mock_pwnam(name):
            if name in valid_users:

                class PwEntry:
                    pw_name = name
                    pw_uid = 1000

                return PwEntry()
            raise KeyError(name)

        return mock_pwnam

    def test_valid_username_accepted(self):
        """A valid username in /etc/passwd should be accepted."""
        with mock.patch.object(self.mod, "pwd") as mock_pwd:
            mock_pwd.getpwnam.side_effect = self._mock_getpwnam(["alice"])
            self.assertTrue(self.mod._is_valid_username("alice"))

    def test_invalid_username_rejected(self):
        """A username not in /etc/passwd should be rejected."""
        with mock.patch.object(self.mod, "pwd") as mock_pwd:
            mock_pwd.getpwnam.side_effect = KeyError("nonexistent")
            self.assertFalse(self.mod._is_valid_username("nonexistent"))

    def test_command_injection_username_rejected(self):
        """
        A crafted username with shell metacharacters should be rejected.
        This is the primary CWE-128 attack vector.
        """
        injection_attempts = [
            "'); rm -rf / #",
            "alice'; rm -rf / #",
            "alice$(whoami)",
            "alice; id",
            "alice`id`",
            "alice && cat /etc/passwd",
            "alice|cat /etc/passwd",
            "alice> /tmp/pwned",
            "alice`rm -rf /`",
            "alice' || true #",
            "$USER",
            "$(id)",
            "`id`",
        ]
        with mock.patch.object(self.mod, "pwd") as mock_pwd:
            mock_pwd.getpwnam.side_effect = KeyError("not found")
            for attempt in injection_attempts:
                with self.subTest(injection_attempt=attempt):
                    self.assertFalse(
                        self.mod._is_valid_username(attempt),
                        f"Username '{attempt}' should be rejected as invalid",
                    )

    def test_empty_username_rejected(self):
        """Empty or None username should be rejected."""
        self.assertFalse(self.mod._is_valid_username(""))
        self.assertFalse(self.mod._is_valid_username(None))

    def test_username_regex_pattern(self):
        """
        The username regex should only allow safe characters.
        Valid: alphanumeric, underscore, hyphen (not at start).
        """
        # Check the regex pattern directly
        pattern = self.mod._VALID_USERNAME_RE
        safe_names = ["alice", "bob123", "user_name", "user-name", "_system"]
        for name in safe_names:
            with self.subTest(safe_name=name):
                self.assertIsNotNone(
                    pattern.match(name),
                    f"Safe username '{name}' should match the pattern",
                )

        unsafe_names = [
            "'; rm -rf / #",
            "$(whoami)",
            "user;id",
            "user`id`",
            "-root",  # starts with hyphen
            "user name",  # space
            "user/name",  # slash
        ]
        for name in unsafe_names:
            with self.subTest(unsafe_name=name):
                self.assertIsNone(
                    pattern.match(name),
                    f"Unsafe username '{name}' should NOT match the pattern",
                )

    def test_get_invoking_user_validates(self):
        """
        get_invoking_user() should validate SUDO_USER against /etc/passwd
        and reject crafted values.
        """
        with mock.patch.object(self.mod, "os") as mock_os:
            with mock.patch.object(self.mod, "pwd") as mock_pwd:
                # SUDO_USER is set to a malicious value
                mock_os.environ = {"SUDO_USER": "'); rm -rf / #", "USER": "root"}
                # Neither matches a valid user
                mock_pwd.getpwnam.side_effect = KeyError("not found")
                mock_os.getuid.return_value = 0

                # Mock getpwuid to return a valid pw_name
                pw_entry = mock.MagicMock()
                pw_entry.pw_name = "root"
                mock_pwd.getpwuid.return_value = pw_entry

                # Should fall back to root since crafted SUDO_USER is invalid
                result = self.mod.get_invoking_user()
                self.assertEqual(result, "root")

    def test_get_invoking_user_accepts_valid_sudo_user(self):
        """
        get_invoking_user() should return SUDO_USER when it's valid.
        """
        with mock.patch.object(self.mod, "os") as mock_os:
            with mock.patch.object(self.mod, "pwd") as mock_pwd:
                mock_os.environ = {"SUDO_USER": "alice", "USER": "root"}

                def mock_pwnam(name):
                    class PwEntry:
                        pw_name = name
                        pw_uid = 1000

                    return PwEntry()

                mock_pwd.getpwnam.side_effect = mock_pwnam
                result = self.mod.get_invoking_user()
                self.assertEqual(result, "alice")


class TestInstallerMethodsNoShellInjection(unittest.TestCase):
    """
    Verify that Installer class methods handling user input do not use
    f-strings in run_command() calls (CWE-78).
    """

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_install_gui_module()
        with open(_INSTALL_GUI_PATH, "r", encoding="utf-8") as f:
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

    def test_clone_repo_no_fstring(self):
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

    def test_install_services_no_fstring(self):
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

    def test_setup_docker_group_no_fstring(self):
        """setup_docker_group() must not use f-string arguments."""
        tree = ast.parse(self.source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "setup_docker_group":
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        func_name = ""
                        if isinstance(child.func, ast.Name):
                            func_name = child.func.id
                        elif isinstance(child.func, ast.Attribute):
                            func_name = child.func.attr
                        if func_name == "run_command":
                            self._assert_no_fstring_arg(child, "setup_docker_group")
                break

    def test_create_env_no_fstring(self):
        """create_env() must not use f-string arguments."""
        tree = ast.parse(self.source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "create_env":
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        func_name = ""
                        if isinstance(child.func, ast.Name):
                            func_name = child.func.id
                        elif isinstance(child.func, ast.Attribute):
                            func_name = child.func.attr
                        if func_name == "run_command":
                            self._assert_no_fstring_arg(child, "create_env")
                break


    def test_start_services_no_fstring(self):
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
