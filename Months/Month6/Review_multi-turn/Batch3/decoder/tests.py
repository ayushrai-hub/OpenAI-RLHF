import jpype
import unittest
from jpype.types import JString
import os

class TestRunLengthCodec(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        path = os.path.join(os.path.dirname(__file__))

        # Start the JVM
        if not jpype.isJVMStarted():
            jpype.startJVM(classpath=[path])

        # Import Java classes
        global IdealCompletion
        IdealCompletion = jpype.JClass('IdealCompletion')

    @classmethod
    def tearDownClass(cls):
        # Shutdown the JVM
        jpype.shutdownJVM()

    def setUp(self):
        # Initialize the RunLengthCodec instance
        self.codec = IdealCompletion.RunLengthCodec()

    # test encoding a valid string.
    def test_encode_valid_string_1(self):
        result = self.codec.encode(JString("AAABBBCC"))
        self.assertEqual(result, "A3B3C2")

    # test encoding a valid string.
    def test_encode_valid_string_2(self):
        result = self.codec.encode(JString("ABCDEFG"))
        self.assertEqual(result, "A1B1C1D1E1F1G1")

    # test if the encoding a valid string works.
    def test_encode_valid_string_3(self):
        result = self.codec.encode(JString("AABBCCCCDDDE"))
        self.assertEqual(result, "A2B2C4D3E1")

    # test if the decoding a fully encoded string works.
    def test_decode_with_fully_encoded_string(self):
        result = self.codec.decode(JString("A2B3C4"))
        self.assertEqual(result, "AABBBCCCC")

    # test if the decoding a fully encoded string works.
    def test_decode_with_partially_encoded_string(self):
        result = self.codec.decode(JString("A3B3CC"))
        self.assertEqual(result, "AAABBBCC")


    # test if the decode function works correctly for partially encoded string with count of 1 missing.
    def test_decode_with_partially_encoded_string_with_missing_single_count(self):
        result = self.codec.decode(JString("A3B3C"))
        self.assertEqual(result, "AAABBBC")

    # test if the encoding validator works for string with lower and upper case mixed.
    def test_can_encode_mixed_letter_case(self):
        self.assertTrue(self.codec.canEncode(JString("ABCabc")))

    # test if the encoding validator works for already fully encoded string.
    def test_can_encode_already_encoded_string(self):
        self.assertFalse(self.codec.canEncode(JString("A1B2C3")))

    # test if the decoding validator works correctly for fully encoded string.
    def test_can_decode_fully_encoded_string(self):
        self.assertTrue(self.codec.canDecode(JString("A2B3C4")))

    # test if the decoding validator works correctly for partially encoded string.
    def test_can_decode_partially_encoded_string(self):
        self.assertTrue(self.codec.canDecode(JString("AAAB3CCCCGG")))        

    # test if the decoding validator works correctly for partially encoded string with count of 1 missing.
    def test_can_decode_partially_encoded_string_with_missing_single_count(self):
        self.assertTrue(self.codec.canDecode(JString("AAAB3CGG")))        

    # test if the decoding validator works correctly for fully encoded string.
    def test_can_decode_invalid_input(self):
        self.assertFalse(self.codec.canDecode(JString("BBBBBCCDD")))

    # test if the encode method raise exception for string with unallowed characters
    def test_encode_invalid_characters(self):
        with self.assertRaises(jpype.JException):
            self.codec.encode(JString("A%B@$C*"))
    
    # test if the decode method raise exception for string with unallowed characters
    def test_decode_invalid_characters(self):
        with self.assertRaises(jpype.JException):
            self.codec.decode(JString("@$A1B*2C3"))


    # test if the encode method raise exception for empty string 
    def test_empty_string_encode(self):
        with self.assertRaises(jpype.JException):
            self.codec.encode(JString(""))

    # test if the decode method raise exception for empty string 
    def test_empty_string_decode(self):
        with self.assertRaises(jpype.JException):
            self.codec.decode(JString(""))

    # test if the encode method raise exception for null input
    def test_null_string_encode(self):
        with self.assertRaises(jpype.JException):
            self.codec.encode(None)

    # test if the decode method raise exception for null input
    def test_null_string_decode(self):
        with self.assertRaises(jpype.JException):
            self.codec.decode(None)

    #  test the method for grouping characters
    def test_group_by_characters(self):
        result = self.codec.groupByCharacters(JString("AAABBBCC"))
        expected = ["AAA", "BBB", "CC"]
        self.assertEqual([str(group) for group in result], expected)

    # test the method for tokenization
    def test_tokenize_valid_input(self):
        tokens = self.codec.tokenize(JString("A3B2C1"))
        token_strings = [(token.character, token.count) for token in tokens]
        expected = [('A', 3), ('B', 2), ('C', 1)]
        self.assertEqual(token_strings, expected)

    # test the method for tokenization where count of 1 is ommited
    def test_tokenize_input_ommited_single_count(self):
        tokens = self.codec.tokenize(JString("A3B2C"))
        token_strings = [(token.character, token.count) for token in tokens]
        expected = [('A', 3), ('B', 2), ('C', 1)]
        self.assertEqual(token_strings, expected)

if __name__ == '__main__':
    unittest.main(verbosity=2)

    