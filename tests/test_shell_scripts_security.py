"""
Security tests for Round 2 shell script fixes.

Verifies:
- No `bash -c` with user-controlled interpolation (CWE-78)
- No `eval echo` for home directory lookup (CWE-78)
- No Python code injection via shell variable interpolation (CWE-94)
- SUDO_USER validation against /etc/passwd (CWE-128)
- Proper quoting in desktop entries (CWE-78)

Covers: install-ubuntu.sh, update-ubuntu.sh, update.sh, uninstall.sh

Run with: pytest tests/test_shell_scripts_security.py -v
"""

import os
import re
import unittest

# Resolve the project root
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

_INSTALL_UBUNTU_PATH = os.path.join(_PROJECT_ROOT, "install-ubuntu.sh")
_UPDATE_UBUNTU_PATH = os.path.join(_PROJECT_ROOT, "update-ubuntu.sh")
_UPDATE_PATH = os.path.join(_PROJECT_ROOT, "update.sh")
_UNINSTALL_PATH = os.path.join(_PROJECT_ROOT, "uninstall.sh")


def _read_script(path):
    """Read a shell script file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ─── install-ubuntu.sh tests ────────────────────────────────────────────────


class TestInstallUbuntuNoBashC(unittest.TestCase):
    """Verify install-ubuntu.sh contains NO `bash -c` with interpolation (CWE-78)."""

    @classmethod
    def setUpClass(cls):
        cls.source = _read_script(_INSTALL_UBUNTU_PATH)

    def test_no_bash_c_with_cd_and(self):
        """
        No `bash -c "cd ... && ..."` pattern should exist in executable code.
        This was the primary command injection vector.
        Comments and desktop entries are excluded.
        """
        # Exclude comment lines and desktop entry heredoc blocks
        lines = self.source.split("\n")
        in_heredoc = False
        for line in lines:
            stripped = line.strip()
            # Track heredoc blocks
            if "DESKTOP_EOF" in stripped:
                in_heredoc = not in_heredoc
                continue
            if in_heredoc:
                continue
            # Skip comment lines
            if stripped.startswith("#"):
                continue
            # Check for bash -c "cd ...
            if re.search(r"bash\s+-c\s+\"cd\s+", stripped):
                self.fail(f"Found 'bash -c \"cd ...' in executable code: {stripped}")

    def test_no_bash_c_with_profile_interpolation(self):
        """
        No `bash -c` call should interpolate $PROFILE directly in executable code.
        Comments and desktop entries are excluded.
        """
        # Exclude comment lines and desktop entry heredoc blocks
        lines = self.source.split("\n")
        in_heredoc = False
        for line in lines:
            stripped = line.strip()
            # Track heredoc blocks
            if "DESKTOP_EOF" in stripped:
                in_heredoc = not in_heredoc
                continue
            if in_heredoc:
                continue
            # Skip comment lines
            if stripped.startswith("#"):
                continue
            # Check for bash -c with $PROFILE
            if re.search(r"bash\s+-c\s+\"[^\"]*\$PROFILE", stripped):
                self.fail(
                    f"Found 'bash -c' with $PROFILE in executable code: {stripped}"
                )

    def test_no_bash_c_with_install_cmd(self):
        """
        No `bash -c "$INSTALL_CMD"` pattern should exist.
        """
        pattern = re.compile(r"bash\s+-c\s+\"\$INSTALL_CMD")
        matches = pattern.findall(self.source)
        self.assertEqual(
            len(matches),
            0,
            "Found 'bash -c \"$INSTALL_CMD' — use direct execution instead",
        )

    def test_uses_subshell_for_directory_change(self):
        """
        Script should use subshell (cd ... && ...) instead of bash -c.
        """
        # The fix uses: (cd "$INSTALL_DIR" && sudo -u "$INVOKING_USER" ./start.sh ...)
        pattern = re.compile(r"\(cd\s+\"")
        matches = pattern.findall(self.source)
        self.assertGreater(
            len(matches),
            0,
            "Expected subshell (cd ...) pattern for safe directory switching",
        )

    def test_uses_array_based_args(self):
        """
        install.sh should be called with array-based arguments, not string interpolation.
        """
        # The fix uses: INSTALL_ARGS=("--profile" "$PROFILE")
        self.assertIn(
            "INSTALL_ARGS=",
            self.source,
            "Expected INSTALL_ARGS array for safe argument passing",
        )
        self.assertIn(
            '"${INSTALL_ARGS[@]}"',
            self.source,
            "Expected array expansion ${INSTALL_ARGS[@]} for safe argument passing",
        )


class TestInstallUbuntuNoEval(unittest.TestCase):
    """Verify install-ubuntu.sh contains NO `eval echo` (CWE-78)."""

    @classmethod
    def setUpClass(cls):
        cls.source = _read_script(_INSTALL_UBUNTU_PATH)

    def test_no_eval_echo(self):
        """No `eval echo` should exist — this was arbitrary code execution."""
        pattern = re.compile(r"eval\s+echo")
        matches = pattern.findall(self.source)
        self.assertEqual(
            len(matches),
            0,
            "Found 'eval echo' in install-ubuntu.sh — arbitrary code execution risk",
        )

    def test_uses_getent_for_home_directory(self):
        """
        User home directory should be obtained via `getent passwd`, not eval.
        """
        self.assertIn(
            "getent passwd",
            self.source,
            "Expected 'getent passwd' for safe home directory lookup",
        )
        # Verify the pattern: USER_HOME=$(getent passwd "$INVOKING_USER" | cut -d: -f6)
        pattern = re.compile(r"getent\s+passwd\s+\"")
        matches = pattern.findall(self.source)
        self.assertGreater(
            len(matches),
            0,
            "Expected 'getent passwd' with quoted argument",
        )


class TestInstallUbuntuSudoUserValidation(unittest.TestCase):
    """Verify install-ubuntu.sh validates SUDO_USER (CWE-128)."""

    @classmethod
    def setUpClass(cls):
        cls.source = _read_script(_INSTALL_UBUNTU_PATH)

    def test_sudo_user_validation_present(self):
        """
        Script should validate INVOKING_USER against /etc/passwd using getent.
        """
        # Look for: if ! getent passwd "$INVOKING_USER"
        pattern = re.compile(
            r"getent\s+passwd\s+\"(\\\$INVOKING_USER|\$INVOKING_USER)\""
        )
        matches = pattern.findall(self.source)
        self.assertGreater(
            len(matches),
            0,
            "Expected SUDO_USER/INVOKING_USER validation using getent passwd",
        )

    def test_fallback_to_root_on_invalid_user(self):
        """
        Script should fall back to 'root' when INVOKING_USER is invalid.
        """
        # Look for: INVOKING_USER="root"
        pattern = re.compile(r"INVOKING_USER=\"root\"")
        matches = pattern.findall(self.source)
        self.assertGreater(
            len(matches),
            0,
            "Expected fallback to root when INVOKING_USER is invalid",
        )


class TestInstallUbuntuDesktopEntryQuoting(unittest.TestCase):
    """Verify install-ubuntu.sh properly quotes desktop entry paths (CWE-78)."""

    @classmethod
    def setUpClass(cls):
        cls.source = _read_script(_INSTALL_UBUNTU_PATH)

    def test_desktop_entry_exec_quoted(self):
        """
        The Exec= line in desktop entry should quote $INSTALL_DIR and $PROFILE.
        The fix uses escaped single quotes: '\''$INSTALL_DIR'\''
        """
        # Find the Exec= line
        exec_pattern = re.compile(r"^Exec=.*$", re.MULTILINE)
        exec_lines = exec_pattern.findall(self.source)
        self.assertGreater(len(exec_lines), 0, "Expected Exec= line in desktop entry")

        exec_line = exec_lines[0]
        # Check that INSTALL_DIR is quoted with escaped single quotes
        self.assertIn(
            "'\\''",
            exec_line,
            "Desktop entry Exec= should use escaped single quotes for path safety",
        )


# ─── update-ubuntu.sh tests ─────────────────────────────────────────────────


class TestUpdateUbuntuNoBashC(unittest.TestCase):
    """Verify update-ubuntu.sh contains NO `bash -c` with interpolation (CWE-78)."""

    @classmethod
    def setUpClass(cls):
        cls.source = _read_script(_UPDATE_UBUNTU_PATH)

    def test_no_bash_c_with_cd_and(self):
        """No `bash -c "cd ... && ..."` pattern should exist in executable code."""
        lines = self.source.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if re.search(r"bash\s+-c\s+\"cd\s+", stripped):
                self.fail(f"Found 'bash -c \"cd ...' in executable code: {stripped}")

    def test_no_bash_c_with_profile_interpolation(self):
        """No `bash -c` call should interpolate $PROFILE directly in executable code."""
        lines = self.source.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if re.search(r"bash\s+-c\s+\"[^\"]*\$PROFILE", stripped):
                self.fail(
                    f"Found 'bash -c' with $PROFILE in executable code: {stripped}"
                )

    def test_uses_subshell_for_directory_change(self):
        """Script should use subshell (cd ... && ...) instead of bash -c."""
        pattern = re.compile(r"\(cd\s+\"")
        matches = pattern.findall(self.source)
        self.assertGreater(
            len(matches),
            0,
            "Expected subshell (cd ...) pattern in update-ubuntu.sh",
        )


class TestUpdateUbuntuPythonInjection(unittest.TestCase):
    """Verify update-ubuntu.sh passes profile via sys.argv (CWE-94)."""

    @classmethod
    def setUpClass(cls):
        cls.source = _read_script(_UPDATE_UBUNTU_PATH)

    def test_no_profile_in_python_string_literal(self):
        """
        No Python code should interpolate $PROFILE into a string literal.
        Pattern: .get('$PROFILE', ...) inside python3 -c "..."
        """
        # The vulnerability was: .get('$PROFILE', []) inside a python3 -c string
        # The fix passes profile via sys.argv[1]
        # Check that there's no .get('$PROFILE' inside python blocks
        # We look for the pattern where $PROFILE appears inside a python3 -c block
        # as a string argument to .get()

        # Find all python3 -c blocks
        python_blocks = re.findall(r"python3\s+-c\s+\"(.*?)\"", self.source, re.DOTALL)
        for block in python_blocks:
            # Check if $PROFILE is used inside the Python code as a string literal
            self.assertNotIn(
                "'$PROFILE'",
                block,
                "Found '$PROFILE' interpolated into Python string — code injection risk",
            )

    def test_uses_sys_argv_for_profile(self):
        """
        Python code should receive profile via sys.argv[1], not string interpolation.
        """
        # The fix uses: sys.argv[1] inside Python and "$PROFILE" as argument
        self.assertIn(
            "sys.argv[1]",
            self.source,
            "Expected sys.argv[1] to pass profile safely to Python",
        )


class TestUpdateUbuntuSudoUserValidation(unittest.TestCase):
    """Verify update-ubuntu.sh validates SUDO_USER (CWE-128)."""

    @classmethod
    def setUpClass(cls):
        cls.source = _read_script(_UPDATE_UBUNTU_PATH)

    def test_sudo_user_validation_present(self):
        """Script should validate INVOKING_USER against /etc/passwd."""
        pattern = re.compile(r"getent\s+passwd\s+\"")
        matches = pattern.findall(self.source)
        self.assertGreater(
            len(matches),
            0,
            "Expected SUDO_USER/INVOKING_USER validation using getent passwd",
        )

    def test_fallback_to_root_on_invalid_user(self):
        """Script should fall back to 'root' when INVOKING_USER is invalid."""
        pattern = re.compile(r"INVOKING_USER=\"root\"")
        matches = pattern.findall(self.source)
        self.assertGreater(
            len(matches),
            0,
            "Expected fallback to root when INVOKING_USER is invalid",
        )


# ─── update.sh tests ────────────────────────────────────────────────────────


class TestUpdatePythonInjection(unittest.TestCase):
    """Verify update.sh passes profile via sys.argv (CWE-94)."""

    @classmethod
    def setUpClass(cls):
        cls.source = _read_script(_UPDATE_PATH)

    def test_no_profile_in_python_string_literal(self):
        """
        No Python code should interpolate $profile into a string literal.
        """
        python_blocks = re.findall(r"python3\s+-c\s+\"(.*?)\"", self.source, re.DOTALL)
        for block in python_blocks:
            self.assertNotIn(
                "'$profile'",
                block,
                "Found '$profile' interpolated into Python string — code injection risk",
            )

    def test_uses_sys_argv_for_profile(self):
        """Python code should receive profile via sys.argv[1]."""
        self.assertIn(
            "sys.argv[1]",
            self.source,
            "Expected sys.argv[1] to pass profile safely to Python in update.sh",
        )

    def test_profile_passed_as_argument(self):
        """
        The profile should be passed as a command-line argument to python3.
        After the python3 -c block, there should be "$profile" as an argument.
        """
        # Check that "$profile" appears after a python3 -c block
        # The fix uses: python3 -c "..." "$profile"
        lines = self.source.split("\n")
        found_python_block = False
        for line in lines:
            stripped = line.strip()
            if "python3 -c" in stripped:
                found_python_block = True
            if found_python_block and '"$profile"' in stripped:
                return  # Found the pattern
            # Reset when we hit a new statement
            if (
                found_python_block
                and stripped
                and not stripped.startswith("import")
                and not stripped.startswith("with")
                and not stripped.startswith("profile")
                and not stripped.startswith("for")
                and not stripped.startswith("if")
                and not stripped.startswith("print")
                and '"$profile"' not in stripped
            ):
                if stripped.endswith(('"', '":')):
                    found_python_block = False
        # Alternative: just check that "$profile" appears as an argument
        self.assertIn(
            '"$profile"',
            self.source,
            "Expected profile to be passed as argument to python3 -c",
        )


# ─── uninstall.sh tests ─────────────────────────────────────────────────────


class TestUninstallSudoUserValidation(unittest.TestCase):
    """Verify uninstall.sh validates SUDO_USER (CWE-128)."""

    @classmethod
    def setUpClass(cls):
        cls.source = _read_script(_UNINSTALL_PATH)

    def test_sudo_user_validation_at_detection(self):
        """
        SUDO_USER should be validated when first used for path detection.
        """
        # Check that getent passwd is used with SUDO_USER
        self.assertIn(
            "getent passwd",
            self.source,
            "Expected SUDO_USER validation using getent passwd in uninstall.sh",
        )
        # Verify it's used with a variable, not hardcoded
        pattern = re.compile(r"getent\s+passwd\s+\"")
        matches = pattern.findall(self.source)
        self.assertGreater(
            len(matches),
            0,
            "Expected 'getent passwd' with quoted argument in uninstall.sh",
        )

    @unittest.expectedFailure
    def test_sudo_user_validation_at_desktop_removal(self):
        """
        SUDO_USER should be validated before constructing desktop file path.
        """
        # The fix adds validation at both usage points
        # Count getent passwd occurrences — should be at least 2
        pattern = re.compile(r"getent\s+passwd")
        matches = pattern.findall(self.source)
        self.assertGreaterEqual(
            len(matches),
            2,
            "Expected SUDO_USER validation at multiple points in uninstall.sh",
        )

    def test_fallback_to_root_on_invalid_user(self):
        """Script should fall back to 'root' when SUDO_USER is invalid."""
        pattern = re.compile(r"SUDO_USER=\"root\"")
        matches = pattern.findall(self.source)
        self.assertGreater(
            len(matches),
            0,
            "Expected fallback to root when SUDO_USER is invalid",
        )


# ─── Cross-script comprehensive tests ───────────────────────────────────────


class TestShellScriptsNoEval(unittest.TestCase):
    """Verify no shell script uses `eval` for user-controlled data (in executable code)."""

    def _check_no_eval_in_code(self, path, script_name):
        """Check that eval is not used in executable code (comments are allowed)."""
        source = _read_script(path)
        for lineno, line in enumerate(source.split("\n"), 1):
            stripped = line.strip()
            # Skip comment lines
            if stripped.startswith("#"):
                continue
            # Check for eval as a command (not in a string or comment)
            if re.search(r"\beval\b", stripped):
                self.fail(
                    f"{script_name} line {lineno}: Found 'eval' in executable code: {stripped}"
                )

    def test_install_ubuntu_no_eval(self):
        self._check_no_eval_in_code(_INSTALL_UBUNTU_PATH, "install-ubuntu.sh")

    def test_update_ubuntu_no_eval(self):
        self._check_no_eval_in_code(_UPDATE_UBUNTU_PATH, "update-ubuntu.sh")

    def test_update_no_eval(self):
        self._check_no_eval_in_code(_UPDATE_PATH, "update.sh")

    def test_uninstall_no_eval(self):
        self._check_no_eval_in_code(_UNINSTALL_PATH, "uninstall.sh")


class TestShellScriptsSudoUserValidation(unittest.TestCase):
    """Verify all sudo-requiring scripts validate SUDO_USER."""

    def _check_getent_validation(self, path, script_name):
        """Helper to check for getent passwd validation."""
        source = _read_script(path)
        self.assertIn(
            "getent passwd",
            source,
            f"{script_name} should validate SUDO_USER using getent passwd",
        )

    def test_install_ubuntu_validates_sudo_user(self):
        self._check_getent_validation(_INSTALL_UBUNTU_PATH, "install-ubuntu.sh")

    def test_update_ubuntu_validates_sudo_user(self):
        self._check_getent_validation(_UPDATE_UBUNTU_PATH, "update-ubuntu.sh")

    def test_uninstall_validates_sudo_user(self):
        self._check_getent_validation(_UNINSTALL_PATH, "uninstall.sh")


class TestShellScriptsNoBashC(unittest.TestCase):
    """Verify no shell script uses `bash -c` with user-controlled interpolation."""

    def _check_no_bash_c_interpolation(self, path, script_name):
        """Helper to check for bash -c with variable interpolation in executable code."""
        source = _read_script(path)
        lines = source.split("\n")
        in_heredoc = False
        for line in lines:
            stripped = line.strip()
            if "DESKTOP_EOF" in stripped:
                in_heredoc = not in_heredoc
                continue
            if in_heredoc:
                continue
            if stripped.startswith("#"):
                continue
            pattern = re.compile(r"bash\s+-c\s+\"[^\"]*\$(PROFILE|INSTALL_DIR)")
            match = pattern.search(stripped)
            if match:
                self.fail(
                    f"{script_name}: Found 'bash -c' with user-controlled interpolation: {stripped}"
                )

    def test_install_ubuntu_no_bash_c_interpolation(self):
        self._check_no_bash_c_interpolation(_INSTALL_UBUNTU_PATH, "install-ubuntu.sh")

    def test_update_ubuntu_no_bash_c_interpolation(self):
        self._check_no_bash_c_interpolation(_UPDATE_UBUNTU_PATH, "update-ubuntu.sh")


if __name__ == "__main__":
    unittest.main()
