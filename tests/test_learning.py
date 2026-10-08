import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('learn', ROOT / 'scripts/learn.py')
learn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(learn)
FORGE = os.environ.get('FORGE', 'forge')


class LearningTests(unittest.TestCase):
    def test_every_lesson_and_challenge_has_identical_native_and_js_output(self):
        course = learn.load_course()
        solutions = learn.load_solutions(course)
        self.assertEqual(len(course['lessons']), 8)
        for lesson in course['lessons']:
            for name, item in [('lesson', lesson), ('challenge', solutions[lesson['id']])]:
                outputs = []
                for backend in ['native', 'js']:
                    with self.subTest(id=lesson['id'], kind=name, backend=backend):
                        output = learn.execute(item['source'], FORGE, backend)
                        self.assertEqual(output, item['expected_output'])
                        outputs.append(output)
                self.assertEqual(outputs[0], outputs[1])

    def test_edited_file_mismatch_is_reported_without_changing_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            edited = Path(temporary) / 'my practice;file.fg'
            source = 'native main { println("my own output"); }'
            edited.write_text(source)
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/learn.py'), '--forge', FORGE,
                                     'run', 'hello', '--file', str(edited)], capture_output=True, text=True, timeout=35)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('my own output', result.stdout)
            self.assertIn('output mismatch', result.stderr)
            self.assertEqual(edited.read_text(), source)

    def test_real_compile_error_and_infinite_loop_do_not_pass(self):
        with self.assertRaises(ValueError):
            learn.execute('native main { let broken: int = ; }', FORGE)
        with self.assertRaises(subprocess.TimeoutExpired):
            learn.execute('native main { while (1) {} }', FORGE, timeout=.1)

    def test_output_limit_and_literal_process_arguments(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = learn.bounded_process([sys.executable, '-c', 'import sys; print(sys.argv[1])', '$(touch sentinel); echo unexpected'], temporary, 3)
            self.assertEqual(output, '$(touch sentinel); echo unexpected\n')
            self.assertFalse((Path(temporary) / 'sentinel').exists())
            with self.assertRaises(ValueError):
                learn.bounded_process([sys.executable, '-c', 'print("x"*70000)'], temporary, 3)

    def test_course_rejects_duplicate_and_incomplete_bilingual_lessons(self):
        good = learn.load_course()
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'course.json'
            duplicate = json.loads(json.dumps(good))
            duplicate['lessons'].append(duplicate['lessons'][0])
            path.write_text(json.dumps(duplicate))
            with self.assertRaises(ValueError):
                learn.load_course(path)
            incomplete = json.loads(json.dumps(good))
            del incomplete['lessons'][0]['explanation']['ko']
            path.write_text(json.dumps(incomplete))
            with self.assertRaises(ValueError):
                learn.load_course(path)


if __name__ == '__main__':
    unittest.main()
