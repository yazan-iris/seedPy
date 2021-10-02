import unittest
import importlib.resources

import Seed


class TestVolume(unittest.TestCase):

    def test_open(self):

        import tarfile
        tar = tarfile.open("sample.tar.gz")

        tar.extractall()
        tar.close()




