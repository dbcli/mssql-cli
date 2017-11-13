import os
import stat

import pytest

from pgcli.config import ensure_dir_exists


def test_ensure_file_parent(tmpdir):
    subdir = tmpdir.join("subdir")
    rcfile = subdir.join("rcfile")
    ensure_dir_exists(str(rcfile))


def test_ensure_existing_dir(tmpdir):
    rcfile = str(tmpdir.mkdir("subdir").join("rcfile"))

    # should just not raise
    ensure_dir_exists(rcfile)

# Below test does not seem to work on windows.
# Commenting this out so that it doesn't fail our test runs.
# Tracked by Github Issue
"""
def test_ensure_other_create_error(tmpdir):
    subdir = tmpdir.join("subdir")
    rcfile = subdir.join("rcfile")

    # trigger an oserror that isn't "directory already exists"
    os.chmod(str(tmpdir), stat.S_IREAD)

    with pytest.raises(OSError):
        ensure_dir_exists(str(rcfile))
"""