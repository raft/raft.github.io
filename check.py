#!/usr/bin/env python3

import difflib
import json
import jsonschema
import sys

schema = json.load(open('implementation.schema.json'))

errors = []
raw_data = open('implementations.json').read()
data = json.loads(raw_data)

for impl in data:
    try:
        jsonschema.validate(impl, schema)
    except jsonschema.exceptions.ValidationError as e:
        errors.append(e)

sorted_data = sorted(data, key=lambda impl: impl['repoURL'])
for expected, actual in zip(sorted_data, data):
    if expected['repoURL'] != actual['repoURL']:
        errors.append(ValueError(
            'Implementations should be sorted by repoURL.\n' +
            f"Expected: {expected['repoURL']}\n" +
            f"Found:    {actual['repoURL']}"))
        break

diff = ''.join(difflib.unified_diff(
    raw_data.splitlines(keepends=True),
    (json.dumps(data, indent=4) + '\n').splitlines(keepends=True),
    fromfile='implementations.json (current)',
    tofile='implementations.json (expected formatting)'))
if diff != '':
    errors.append(ValueError('Formatting error:\n' + diff))

# Saving the file without a trailing newline is a common error. It's already
# caught by difflib above, but this error message is clearer.
if not raw_data.endswith(']\n'):
    errors.append(ValueError('implementations.json should end in one \\n'))

if errors:
    print(f'Encountered {len(errors)} errors:')
    for error in errors:
        print()
        print(error)
    sys.exit(1)
