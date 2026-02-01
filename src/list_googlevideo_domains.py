from collections.abc import Generator, Iterable
import argparse
import logging
import pathlib
import random
import re
import sys
import time

import requests

import constants


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)


URL_RE = re.compile(r'https://(rr\d+--.{,50}\.googlevideo\.com)')


def get_youtube_search_results(search_query: str) -> str:
    return requests.get(
        'https://www.youtube.com/results',
        params={'search_query': search_query},
    ).text


def load_multiline_file(filepath: pathlib.Path) -> Generator[str, None, None]:
    with open(filepath, encoding='utf-8') as f:
        while line := f.readline():
            yield line.strip('\n')


def dump_multiline_file(lines: Iterable[str], filepath: pathlib.Path):
    with open(filepath, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(f'{line}\n')


def parse_args(raw_args: Iterable[str]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--queries',
        type=pathlib.Path,
        default=constants.YOUTUBE_SEARCH_QUERIES_PATH,
    )
    parser.add_argument(
        '--domains',
        type=pathlib.Path,
        default=constants.GOOGLEVIDEO_DOMAINS_PATH,
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=0.5,
    )
    return parser.parse_args(raw_args)


def main():
    args = parse_args(sys.argv[1:])
    random.seed(time.time())

    queries = list(load_multiline_file(args.queries))
    random.shuffle(queries)

    old_domains = set(
        load_multiline_file(args.domains) if args.domains.exists() else []
    )
    new_domains = set()
    for query in queries:
        logging.info('Fetching googlevideo domains for "%s"', query)
        try:
            search_results = get_youtube_search_results(query)
        except Exception:
            logging.exception(
                'Failed to get youtube search results for "%s"', query
            )
            continue
        new_domains.update(URL_RE.findall(search_results))

        logging.info('Sleeping for %.2f before next query...', args.delay)
        time.sleep(args.delay)

    logging.info('Fetched %d new domains', len(new_domains - old_domains))
    dump_multiline_file(sorted(old_domains | new_domains), args.domains)


if __name__ == '__main__':
    main()
