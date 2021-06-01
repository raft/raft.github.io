The Raft Consensus Algorithm
============================

This is the repo for the Raft website: https://raft.github.io

Please contribute to the website by submitting pull requests (preferably) or
creating issues. The most common way people contribute is by adding a new
implementation to `implementations.json`. Note that the file is ordered
lexicographically by GitHub repo URL, and this is strictly enforced by automated
checks.

When you submit a PR, `./check.py` will make sure the data is well-formed. If
you want to run it locally, you'll need the
[`jsonschema`](https://pypi.org/project/jsonschema/) library first:
```
pip3 install jsonschema
```

You can use a Python virtual environment if you are unable to or don't want to
install jsonschema globally. See <https://docs.python.org/3/tutorial/venv.html>
for instructions.

The website is hosted as a GitHub static page at <https://raft.github.io>. To
run it locally, make sure you've checked out all the submodules:
```
git submodule update --init --recursive
```

Then start a local static webserver:
```
python3 -m http.server 8000 --bind localhost
```
and open <http://localhost:8000/>. The server is needed to allow `index.html` to
pull down `implementations.json`.

The implementations are sorted on the website according to GitHub stars and last
update time. This information is cached on a separate server a few times a day,
so new implementations will initially appear at the bottom of the table for a
few hours.

This work is licensed under a Creative Commons Attribution 3.0 Unported License.
See https://creativecommons.org/licenses/by/3.0/deed.en_US for details.
