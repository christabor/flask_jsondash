"""A python runner for nodejs test files."""

import os
import subprocess
import sys


def check_tests():
    """Run all tests."""
    js_files = [f for f in os.listdir('.') if f.endswith('Spec.js')]
    results = dict()
    for spec in js_files:
        results[spec] = subprocess.call(['jasmine', spec])
    all_passed = sum(results.values()) == 0
    return all_passed


if __name__ == '__main__':
    # Return a standard exit code for CI pipelines to use.
    code = 1 if not check_tests() else 0
    print('=' * 80)
    print('Test results: {}'.format('passed' if code == 0 else 'failed!'))
    print('=' * 80)
    sys.exit(code)
