import unittest
from client import client


class MyTestCase(unittest.TestCase):
    def test_client(self):
        c = client()



if __name__ == '__main__':
    unittest.main()
