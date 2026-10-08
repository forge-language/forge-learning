#!/usr/bin/env python3
"""Read and run the Forge beginner course with an explicitly installed compiler."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MAX_OUTPUT = 65536


def load_course(path=ROOT / 'course.json'):
    course = json.loads(Path(path).read_text())
    if course.get('schema_version') != 1 or not isinstance(course.get('lessons'), list) or not course['lessons']:
        raise ValueError('Course must contain schema_version 1 and lessons')
    seen = set()
    for lesson in course['lessons']:
        identity = lesson.get('id', '')
        if not isinstance(identity, str) or not re.fullmatch(r'[a-z][a-z0-9-]*', identity) or identity in seen:
            raise ValueError('Lesson IDs must be unique safe identifiers')
        seen.add(identity)
        for field in ['title', 'summary', 'explanation', 'challenge']:
            if not isinstance(lesson.get(field), dict) or any(not isinstance(lesson[field].get(language), str) or not lesson[field][language].strip() for language in ['en', 'ko']):
                raise ValueError('Lesson ' + identity + ' lacks bilingual ' + field)
        if not isinstance(lesson.get('source'), str) or not lesson['source'].strip() or not isinstance(lesson.get('expected_output'), str):
            raise ValueError('Lesson ' + identity + ' lacks source or expected output')
    return course


def load_solutions(course):
    data = json.loads((ROOT / 'solutions.json').read_text())
    items = data.get('lessons', [])
    if data.get('schema_version') != 1 or not isinstance(items, list):
        raise ValueError('Malformed challenge solutions')
    mapping = {}
    for item in items:
        if item.get('id') in mapping or not isinstance(item.get('source'), str) or not isinstance(item.get('expected_output'), str):
            raise ValueError('Malformed or duplicate challenge solution')
        mapping[item['id']] = item
    if set(mapping) != {lesson['id'] for lesson in course['lessons']}:
        raise ValueError('Every lesson must have one challenge solution')
    return mapping


def bounded_process(command, directory, timeout):
    """No shell; redirect output to disk so a loop cannot exhaust Python memory."""
    with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
        result = subprocess.run(command, cwd=directory, stdin=subprocess.DEVNULL,
                                stdout=output, stderr=errors, timeout=timeout, shell=False)
        if output.tell() > MAX_OUTPUT or errors.tell() > MAX_OUTPUT:
            raise ValueError('Program output exceeds the 64 KiB limit')
        output.seek(0)
        errors.seek(0)
        stdout, stderr = output.read().decode(), errors.read().decode(errors='replace')
        if result.returncode:
            raise ValueError('Command failed (' + str(result.returncode) + '): ' + stderr)
        return stdout


def execute(source, compiler='forge', backend='native', timeout=3, node='node'):
    if backend not in ['native', 'js']:
        raise ValueError('Backend must be native or js')
    if not isinstance(source, str) or len(source.encode()) > 65536:
        raise ValueError('Source must be a string of at most 64 KiB')
    compiler_path = shutil.which(str(compiler))
    if not compiler_path:
        raise ValueError('Forge compiler not found; install the SDK or pass --forge /path/to/forge')
    compiler_path = str(Path(compiler_path).resolve())
    with tempfile.TemporaryDirectory(prefix='forge-learning-') as directory:
        root = Path(directory)
        source_path = root / 'lesson.fg'
        source_path.write_text(source)
        output_path = root / ('lesson.cjs' if backend == 'js' else 'lesson')
        command = [compiler_path, str(source_path), '-o', str(output_path)]
        if backend == 'js':
            command.append('--emit-js')
        bounded_process(command, directory, 30)
        if backend == 'js':
            node_path = shutil.which(str(node))
            if not node_path:
                raise ValueError('Node.js is required for --backend js')
            command = [str(Path(node_path).resolve()), str(output_path)]
        else:
            command = [str(output_path)]
        return bounded_process(command, directory, timeout)


def check_output(actual, expected, identity):
    if actual != expected:
        raise ValueError(identity + ' output mismatch: expected ' + repr(expected) + ', received ' + repr(actual))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--forge', default='forge', help='Installed compiler executable; never built or downloaded by this runner')
    parser.add_argument('--language', choices=['en', 'ko'], default='en')
    commands = parser.add_subparsers(dest='action', required=True)
    commands.add_parser('list')
    show = commands.add_parser('show')
    show.add_argument('id')
    run = commands.add_parser('run')
    run.add_argument('id')
    run.add_argument('--backend', choices=['native', 'js'], default='native')
    run.add_argument('--file', type=Path, help='Run your edited local .fg file against this lesson output')
    run.add_argument('--solution', action='store_true', help='Run the reference challenge solution and check its challenge output')
    check = commands.add_parser('check')
    check.add_argument('--backend', choices=['native', 'js', 'both'], default='both')
    args = parser.parse_args()
    try:
        course = load_course()
        if args.action == 'list':
            for lesson in course['lessons']:
                print(lesson['id'] + ': ' + lesson['title'][args.language])
            return
        if args.action == 'check':
            solutions = load_solutions(course)
            backends = ['native', 'js'] if args.backend == 'both' else [args.backend]
            for lesson in course['lessons']:
                for name, item in [('lesson', lesson), ('challenge', solutions[lesson['id']])]:
                    for backend in backends:
                        check_output(execute(item['source'], args.forge, backend), item['expected_output'], lesson['id'] + '/' + name + '/' + backend)
                        print('PASS ' + lesson['id'] + '/' + name + '/' + backend)
            return
        lesson = next((item for item in course['lessons'] if item['id'] == args.id), None)
        if lesson is None:
            raise ValueError('Unknown lesson; use list to see IDs')
        if args.action == 'show':
            print(lesson['title'][args.language] + '\n\n' + lesson['explanation'][args.language] + '\n\n' + lesson['source'])
            print('Expected output:\n' + lesson['expected_output'] + '\nChallenge: ' + lesson['challenge'][args.language])
            return
        item = load_solutions(course)[args.id] if args.solution else lesson
        source = args.file.read_text() if args.file else item['source']
        actual = execute(source, args.forge, args.backend)
        print(actual, end='')
        check_output(actual, item['expected_output'], args.id)
        print('PASS: output matches')
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
