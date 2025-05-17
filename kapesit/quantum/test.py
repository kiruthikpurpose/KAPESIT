import unittest
import subprocess
import os

class TestQuantumImplementations(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.results = {}

    def test_cpp_implementation(self):
        cpp_dir = os.path.join(self.test_dir, 'cpp')
        result = subprocess.run(['./quantum_cpp'], cwd=cpp_dir, capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.results['cpp'] = result.stdout.decode()

    def test_java_implementation(self):
        java_dir = os.path.join(self.test_dir, 'java')
        result = subprocess.run(['java', 'QuantumTest'], cwd=java_dir, capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.results['java'] = result.stdout.decode()

    def test_go_implementation(self):
        go_dir = os.path.join(self.test_dir, 'go')
        result = subprocess.run(['./quantum_go'], cwd=go_dir, capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.results['go'] = result.stdout.decode()

    def test_csharp_implementation(self):
        csharp_dir = os.path.join(self.test_dir, 'csharp')
        result = subprocess.run(['dotnet', 'run'], cwd=csharp_dir, capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.results['csharp'] = result.stdout.decode()

    def test_asm_implementation(self):
        asm_dir = os.path.join(self.test_dir, 'asm')
        result = subprocess.run(['./quantum_asm'], cwd=asm_dir, capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.results['asm'] = result.stdout.decode()

    def tearDown(self):
        # Clean up test results
        for lang in ['cpp', 'java', 'go', 'csharp', 'asm']:
            lang_dir = os.path.join(self.test_dir, lang)
            if os.path.exists(lang_dir):
                for item in os.listdir(lang_dir):
                    if item.endswith(('.o', '.exe', '.so', '.dll', '.class')):
                        os.remove(os.path.join(lang_dir, item))

if __name__ == '__main__':
    unittest.main()
