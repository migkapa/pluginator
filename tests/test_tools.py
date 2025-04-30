import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools import log_planning, log_start_writing_files, log_finish_writing_files, log_checking_compliance, log_testing_plugin

class TestLoggingTools(unittest.TestCase):
    
    @patch('tools.logger.info')
    def test_log_planning(self, mock_logger):
        result = log_planning()
        mock_logger.assert_called_once_with("Planning...")
        self.assertEqual(result, "Logged planning stage.")
    
    @patch('tools.logger.info')
    def test_log_start_writing_files(self, mock_logger):
        result = log_start_writing_files()
        mock_logger.assert_called_once_with("Writing files...")
        self.assertEqual(result, "Logged start of file writing.")
    
    @patch('tools.logger.success')
    def test_log_finish_writing_files(self, mock_logger):
        result = log_finish_writing_files()
        mock_logger.assert_called_once_with("Finished writing files.")
        self.assertEqual(result, "Logged finish of file writing.")
    
    @patch('tools.logger.info')
    def test_log_checking_compliance(self, mock_logger):
        result = log_checking_compliance()
        mock_logger.assert_called_once_with("Checking compliance...")
        self.assertEqual(result, "Logged start of compliance check.")
    
    @patch('tools.logger.info')
    def test_log_testing_plugin(self, mock_logger):
        result = log_testing_plugin()
        mock_logger.assert_called_once_with("Activating plugin simulation...")
        self.assertEqual(result, "Logged start of plugin testing.")

if __name__ == '__main__':
    unittest.main() 