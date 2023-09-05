import unittest


import libs.cli_tools as cli_tools


# Test cases
#=======================================================================================================================
class TestFunctionIsToolInstalled(unittest.TestCase):
    def test_non_installed_tool(self):
        b_installed = cli_tools.is_tool_installed('whatever')
        s_msg = 'A non-installed tool is detected as installed.'
        self.assertFalse(b_installed, s_msg)

    def test_installed_tool(self):
        b_installed = cli_tools.is_tool_installed('date')
        s_msg = 'A installed tool is detected as non installed.'
        self.assertTrue(b_installed, s_msg)


# Main code
#=======================================================================================================================
if __name__ == '__main__':
    unittest.main()
