#!/usr/bin/env python3

# This script is under the public domain.

import base64
import json
import os
import re
import time
from urllib.error import URLError
from urllib.request import urlopen, Request

"""
Possibly interesting fields:
- created_at
- description
- forks_count
- homepage
- pushed_at
- size
- stargazers_count
- subscribers_count
- updated_at
- watchers_count
"""
def get_repo(repo_id):
    if repo_id is None:
        return None
    headers = {}
    url = 'https://api.github.com/repos/%s' % repo_id

    # Expected format: username:hexadecimalpersonalaccesstoken.
    try:
        credentials = os.environ['GITHUB_TOKEN']
    except KeyError:
        pass
    else:
        credentials = base64.b64encode(bytes(credentials, 'utf-8'))
        headers['Authorization'] = b'Basic ' + credentials

    try:
        response = urlopen(Request(url, headers=headers))
    except URLError as e:
        print(f'Warning: Fetching {url} failed: {e.reason}')
        try:
            print(json.load(e))
        except:
            pass
        return None
    else:
        content = json.load(response)
        return content

def days_since(timestr):
    now = time.mktime(time.gmtime())
    then = time.mktime(time.strptime(timestr, '%Y-%m-%dT%H:%M:%SZ'))
    return (now - then) / 60 / 60 / 24

def get_repo_score(repo):
    return repo.get('stargazers_count', 0)

def repo_url_to_id(url):
    if url is None:
        return None
    m = re.match(r'https://github.com/([^/#]+/[^/#]+)/?', url)
    if m is None:
        return None
    else:
        return m.group(1)

def get_all_repos():
    response = urlopen('https://raft.github.io/implementations.json')
    impls = json.load(response)
    urls = [impl['repoURL'] for impl in impls]
    repos = [(url, get_repo(repo_url_to_id(url)))
             for url in urls]
    repos = [(url, repo)
             for url, repo in repos
             if repo is not None]
    return repos

def rank(repos, sort_key, result_key):
    for rank, (_url, repo) in enumerate(sorted(repos,
                                        key=lambda repo: sort_key(repo[1]))):
        repo[result_key] = rank

def main(filename='repos.jsonp'):
    repos = get_all_repos()
    rank(repos,
         sort_key=lambda repo: repo.get('stargazers_count', 0),
         result_key='stars_rank')
    rank(repos,
         sort_key=lambda repo: repo.get('updated_at', '1970-01-01T00:00:00Z'),
         result_key='updated_rank')
    for _url, repo in repos:
        repo['rank'] = repo['stars_rank'] + repo['updated_rank']
    repos.sort(key=lambda repo: repo[1]['rank'], reverse=True)
    f = open(filename, 'w')
    f.write('var raft_repos = function() {\n')
    f.write('return ')
    json.dump(dict([(url,
                     {'rank': repo['rank'],
                      'stars': repo['stargazers_count'],
                      'updated': repo['updated_at']})
                     for (url, repo) in repos]),
              f,
              indent=4)
    f.write(';\n')
    f.write('};\n')

if __name__ == '__main__':
    main()
