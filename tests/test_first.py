import unittest
from flask_apps.app import app

class TestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_hello_world(self):

        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), '<h2>Hello, World!</h2>')

        response = self.app.get('/?arg=John')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), '<h2>Hello, John!</h2>')

        response = self.app.get('/?arg=Cena')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), '<h2>Hello, Cena!</h2>')




if __name__ == '__main__':
    unittest.main()