import unittest
from modernizer.cli import annotate, parse_diagnostics, sources
from pathlib import Path
from tempfile import TemporaryDirectory

class ModernizerTests(unittest.TestCase):
    def test_parse(self):
        diagnostics = '/tmp/demo.cpp:3:9: warning: use nullptr [modernize-use-nullptr]'
        result = parse_diagnostics(diagnostics)
        self.assertEqual(result[0]['line'], 3)
        self.assertEqual(result[0]['check'], 'modernize-use-nullptr')

    def test_annotate(self):
        result = annotate('int x;\nint y;\n', [{'line': 2, 'message': 'test', 'check': 'demo'}])
        self.assertIn('// clang-tidy [demo]: test\nint y;', result)

    def test_sources(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'a.cpp').write_text('int x;')
            (root / 'ignore.txt').write_text('hi')
            self.assertEqual([p.name for p in sources(root)], ['a.cpp'])

if __name__ == '__main__':
    unittest.main()
