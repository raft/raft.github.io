#!/usr/bin/env python2

# This script is under the public domain.

from bs4 import BeautifulSoup
import json
import os
import re
import time
import urllib2

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
    api_url = 'https://api.github.com/repos/%s' % repo_id
    try:
        api_url2 = '%s?access_token=%s' % (api_url, os.environ['GITHUB_TOKEN'])
    except KeyError:
        api_url2 = api_url

    try:
        response = urllib2.urlopen(api_url2)
    except urllib2.HTTPError, e:
        print 'Warning: URL %s returned status %d' % (api_url, e.code)
        try:
            print json.load(e)
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
    m = re.match(r'https?://github.com/([^/]+/[^/]+)/?', url)
    if m is None:
        return None
    else:
        return m.group(1)

def get_all_urls():
    response = urllib2.urlopen('http://raft.github.io')
    content = BeautifulSoup(response)
    urls = [link.get('href') for link in content.find_all('a')]
    return list(set(urls))

def get_all_repos():
    urls = get_all_urls()
    repos = [(url, get_repo(repo_url_to_id(url)))
             for url in urls]
    repos = [(url, repo)
             for url, repo in repos
             if repo is not None]
    return repos

def rank(repos, sort_key, result_key, reverse=False):
    for rank, (url, repo) in enumerate(sorted(repos,
                                       key=lambda (url, repo): sort_key(repo),
                                       reverse=reverse)):
        repo[result_key] = rank

def main(filename='repos.jsonp'):
    repos = get_all_repos()
    rank(repos,
         sort_key=lambda repo: repo.get('stargazers_count', 0),
         result_key='stars_rank')
    rank(repos,
         sort_key=lambda repo: repo.get('updated_at', '1970-01-01T00:00:00Z'),
         result_key='updated_rank')
    for url, repo in repos:
        repo['rank'] = repo['stars_rank'] + repo['updated_rank']
    repos.sort(key=lambda (url, repo): repo['rank'], reverse=True)
    f = open(filename, 'w')
    f.write('var raft_repos = function() {\n')
    f.write('return ')
    json.dump(dict([(url,
                     {'rank': repo['rank'],
                      'stars': repo['stargazers_count'],
                      'updated': repo['updated_at']})
                     for (url, repo) in repos]),
              f)
    f.write(';\n')
    f.write('};\n')

if __name__ == '__main__':
    main()
