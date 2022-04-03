import unittest
from unittest import TestCase

from client import client, Client

HOST = '127.0.0.1'
PORT = 55000


""" manually run the server with port 55000 with ID:"Dvir" """
class MyTestCase(unittest.TestCase):
    class test_client(TestCase):


        def Initialize_client_port(self):
            self.c = Client(HOST, PORT)
            self.assertEqual(self.c.port, 55000)

        def ID(self):
            self.assertEqual(self.c.id, "Dvir")



if __name__ == '__main__':
    unittest.main()
