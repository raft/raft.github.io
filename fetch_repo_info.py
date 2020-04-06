#!/usr/bin/python3
import logging
from time import ctime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

AUTHENTICATION_TOKEN = '<<<PUT YOUR TOKEN HERE>>>'

ENDPOINT = 'https://api.github.com/graphql'

GQ_LOGIN = """
{
  viewer {
    login
  }
}
"""

GQ_GETREPO = """
{
  repository(owner: "<o>", name: "<n>") {
    url
    homepageUrl
    description
    createdAt
    updatedAt
    pushedAt
    forkCount
    watchers {
      totalCount
    }
    primaryLanguage {
      name
    }
    stargazers {
      totalCount
    }
    licenseInfo {
      name
    }
    nameWithOwner
    diskUsage
  }
}
"""


def extract_metadata_from_url(url):
    print(f"[{ctime()}] {url}")

    resp = requests.head(url)
    while resp.status_code == 301:
        url = resp.headers['location']
        resp = requests.head(url)

    parsed = urlparse(resp.url) if resp.status_code == 200 else urlparse(url)

    if parsed.netloc == 'github.com':
        parts = parsed.path.split('/')
        return {
            'url': resp.url,
            'netloc': parsed.netloc,
            'owner': parts[1],
            'name': parts[2]
        }
    else:
        return {
            'url': resp.url,
            'netloc': parsed.netloc
        }


def fetch_detail(session, metadata):
    if metadata['netloc'] != 'github.com':
        return {'request': metadata}
    else:
        print(f"[{ctime()}] {metadata['owner']} {metadata['name']}")

        query = GQ_GETREPO \
            .replace('<n>', metadata['name']) \
            .replace('<o>', metadata['owner'])

        resp = session.post(ENDPOINT, json={'query': query}).json()
        resp['request'] = metadata
        return resp


def process_repo_detail(repo):
    for key in ['watchers', 'stargazers']:
        repo[key] = repo[key]['totalCount'] if isinstance(
            repo[key], dict) else repo[key]

    for key in ['primaryLanguage', 'licenseInfo']:
        repo[key] = repo[key]['name'] if isinstance(
            repo[key], dict) else repo[key]

    return repo


def main():
    ############################################################################
    print('=\n== GET ALL PROJECTS FROM http://raft.github.io ===')
    ############################################################################

    resp = requests.get('http://raft.github.io')
    assert(resp.status_code == 200)
    soup = BeautifulSoup(resp.content, 'html.parser')
    table_rows = soup.find('table', id='implementations').find_all('tr')
    urls = map(lambda tr: tr.find('td').find('a').get('href'), table_rows[1:])

    projects = [extract_metadata_from_url(url) for url in set(urls)]

    ############################################################################
    print(f'\n=== GET DETAILS FROM {ENDPOINT} ===')
    ############################################################################

    session = requests.session()
    session.headers['Authorization'] = f'bearer {AUTHENTICATION_TOKEN}'

    resp = session.post(ENDPOINT, json={'query': GQ_LOGIN})
    assert(resp.status_code == 200 and 'errors' not in resp.json())

    details = [fetch_detail(session, metadata) for metadata in projects]

    ############################################################################
    print(f'\n=== PROCESS DETAILS ===')
    ############################################################################

    github = []
    errors = []
    others = []
    for detail in details:
        if 'errors' in detail:
            errors.append(detail)
            continue

        if 'data' not in detail:
            others.append(detail)
            continue

        process_repo_detail(detail['data']['repository'])
        github.append(detail)

    print(errors)
    return github, others, errors


if __name__ == "__main__":
    import json

    g, o, e = main()

    print(f'=== DUMP TO FILES ===')
    with open('raft_projects.json', 'w') as f:
        json.dump({
            'github': g,
            'others': o,
            'errors': e
        }, f)

    import pandas as pd
    data = [item['data'] for item in g]
    df = pd.DataFrame(data)
    df.to_excel('raft_github.xlsx')
