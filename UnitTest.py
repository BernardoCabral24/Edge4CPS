import unittest
import unittest.mock
from ImageCompatibility import main_task
from ApiFerrovia import port_text_beautify, port_to_text

class MainTaskTestCase(unittest.TestCase):

    def test_image_compatibility_right(self):
        result = main_task("nginx")
        self.assertEqual(result, "amd")

    def test_image_compatibility_bad_parameters(self):
        result = main_task("something-wrong")
        self.assertEqual(result, [])

    def test_port_text_beautify(self):
        result = port_text_beautify("8080")
        self.assertIn("8080|",result)

    def test_port_text_beautify_wrong(self):
        with self.assertRaises(AssertionError):
            result = port_text_beautify("")
            self.assertIn("8080|",result)

    def test_port_text_beautify_multiple(self):
        result = port_text_beautify('       - "10001:8080"       - "10002:20022"')
        self.assertIn('|10001:8080"|10002:20022"|',result)

    def test_port_to_text_single(self):
        result = port_to_text([8080])
        self.assertEqual(len(result.split("-")),2)

    def test_port_to_text_multiple(self):
        result = port_to_text([8080,2020])
        self.assertEqual(len(result.split("-")),3)

    def test_port_to_text_empty(self):
        result = port_to_text([])
        self.assertEqual(result, "")

if __name__ == '__main__':
    unittest.main()
