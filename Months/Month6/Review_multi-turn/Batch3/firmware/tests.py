import unittest
import execjs
import os

class TestBeetleMovement(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        js_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'ideal_completion.js'))
        with open(js_file_path, 'r') as file:
            cls.js_code = file.read()
        cls.ctx = execjs.compile(cls.js_code)

    # Test default MFMFirmware for unspecified site numbers, to ensure it uses the default firmware
    def test_get_mfm_firmware_default(self):
        result = self.ctx.call('getMFMFirmware', 1000)
        self.assertEqual(result, 'A29D.4865', "Default firmware should be 'A29D.4865' for unknown site numbers")

    # Test for the specific site numbers, to ensure the code returns the different firmware.
    def test_get_mfm_firmware_specific(self):
        for site_number in [1631, 1632, 1701, 1702]:
            result = self.ctx.call('getMFMFirmware', site_number)
            self.assertEqual(result, 'df21.4865', f"Firmware should be 'df21.4865' for site number {site_number}")

    # Test default MFMFirmware without site numbers, to ensure it uses the default firmware
    def test_get_mfm_firmware_no_site_number(self):
        result = self.ctx.call('getMFMFirmware')
        self.assertEqual(result, 'A29D.4865', "Default firmware should be 'A29D.4865' for no site numbers")

if __name__ == '__main__':
    unittest.main()
