import unittest
from flask_apps.first import hello_world

class TestCase(unittest.TestCase):

    def test_hello_world(self):
        result = hello_world()
        self.assertEqual(result, '<p>Hello, World! working</p>')

if __name__ == '__main__':
    unittest.main()