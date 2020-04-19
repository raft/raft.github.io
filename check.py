#!/usr/bin/env python3

import json
import jsonschema

schema = json.load(open('implementation.schema.json'))

raw_data = open('implementations.json').read()
if not raw_data.endswith(']\n'):
    raise ValueError('implementations.json should end in one \\n')
data = json.loads(raw_data)

for impl in data:
    jsonschema.validate(impl, schema)

sorted_data = sorted(data, key=lambda impl: impl['repoURL'])
for expected, actual in zip(sorted_data, data):
    if expected['repoURL'] != actual['repoURL']:
        print('Expected:', expected['repoURL'])
        print('Found:   ', actual['repoURL'])
        raise ValueError('Implementations should be sorted by repoURL')

