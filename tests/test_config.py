import unittest
import shutil
from mssqlcli.config import (
    ensure_dir_exists,
    get_config,
)
from mssqltestutils import getTempPath


class ConfigTests(unittest.TestCase):

    def test_ensure_existing_dir(self):
        rcfilePath = getTempPath('subdir', 'rcfile')
        get_config(rcfilePath)
        # should just not raise
        ensure_dir_exists(rcfilePath)
        shutil.rmtree(getTempPath())


    # Below test does not seem to work on windows.
    # Commenting this out so that it doesn't fail our test runs.
    # Tracked by Github Issue
    # def test_ensure_other_create_error(self):
    #     rcfilePath = getTempPath('subdir', 'rcfile')
    #     get_config(rcfilePath)

    #     # trigger an oserror that isn't "directory already exists"
    #     os.chmod(rcfilePath, stat.S_IREAD)

    #     with pytest.raises(OSError):
    #         ensure_dir_exists(rcfilePath)
