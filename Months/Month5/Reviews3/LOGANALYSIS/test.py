import unittest
import logging
import subprocess
from ideal_completion import log_epoch

# Configure the logger
logging.basicConfig(
    filename='Logs_of_training.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger()

class TestLogger(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.command = 'grep -E "BiLSTM|CNN|epoch" Logs_of_training.txt'
        
    @classmethod
    def tearDownClass(cls):
        cls.run_command('rm Logs_of_training.txt')
        
    @classmethod
    def run_command(cls, command):
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        return result.stdout, result.stderr
        
    def test_no_error(self):
        epochs = [1, 2, 3]
        losses = [0.1, 0.2, 0.3]
        accuracies = [0.9, 0.8, 0.7]
        
        log_epoch(logger, epochs, losses, accuracies)
        
        stdout, stderr = self.run_command(self.command)
        self.assertEqual(stderr, '')

    def test_log_epoch(self):
        epochs = [1, 2, 3]
        losses = [0.1, 0.2, 0.3]
        accuracies = [0.9, 0.8, 0.7]
        
        log_epoch(logger, epochs, losses, accuracies)
        
        stdout, _ = self.run_command(self.command)
        self.assertTrue(len(stdout) > 0)
        
if __name__ == '__main__':
    unittest.main()