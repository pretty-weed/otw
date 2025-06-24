#!/usr/bin/env python3

from argparse import ArgumentParser
import html.parser
from pathlib import Path

import requests

PathType = type(Path)
MAX_BANDIT = 34
WARGAMES_URL = "https://overthewire.org/wargames/"
BANDIT_URL = WARGAMES_URL + "bandit/"


class Parser(html.parser.HTMLParser):
    def __init__(self, *, convert_charrefs=True):
        self.in_content = False
        self.sub_divs = 0
        self.content = ""
        self._ignore = 0
        return super().__init__(convert_charrefs=convert_charrefs)

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self._ignore += 1
        elif tag == "div":

            attr_dict = dict(attrs)
            if attr_dict.get("id") == "content":
                self.in_content = True

            elif self.in_content:
                self.sub_divs += 1

    def handle_endtag(self, tag):
        if tag == "script":
            assert self._ignore
            self._ignore -= 1
        elif tag == "div":

            if self.sub_divs:
                self.sub_divs -= 1
            elif self.in_content:
                self.in_content = False

    def handle_data(self, data):
        if self.in_content and not self._ignore:
            self.content += data

    def feed_me(self, feed: str) -> str:
        self.content = ""
        self.feed(feed)
        return self.content


def format(directions_path: PathType) -> None:

    pass


def main():
    arg_parser = ArgumentParser()
    subparsers = arg_parser.add_subparsers(required=False)
    fetch_parser = subparsers.add_parser("fetch")
    fetch_parser.set_defaults(action="fetch")
    arg_parser.set_defaults(action="fetch")
    format_parser = subparsers.add_parser("format")
    format_parser.set_defaults(action="format")
    format_parser.add_argument("source", nargs="?", default="instructions")
    arg_parser.add_argument("dest", nargs="?", default="instructions")
    fetch_parser.add_argument("--format", action="store_true")

    arg_parser.set_defaults(action="fetch")
    parsed = arg_parser.parse_args()
    dest_dir = Path(parsed.dest)
    if not dest_dir.exists():
        dest_dir.mkdir()
    elif not dest_dir.is_dir():
        arg_parser.error(f"{dest_dir} is not a dir")

    files = None
    if parsed.action == "fetch":
        parsed.source = parsed.dest
        html_parser = Parser()
        files = []
        for level in range(MAX_BANDIT + 1):
            level_url = BANDIT_URL + f"bandit{level}.html"
            res = requests.get(level_url)
            files.append(dest_dir.joinpath(f"bandit{level-1}-to-{level}.txt"))
            files[-1].write_text(html_parser.feed_me(res.content.decode()).strip() + "\n")
    if parsed.action == "format" or parsed.format:
        for file in files if files is not None else dest_dir.glob("*.txt"):
            print(file)
            print(file.read_text())
            print()


if __name__ == "__main__":
    main()
