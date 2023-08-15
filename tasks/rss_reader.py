# You shouldn't change  name of function or their arguments,
# but you can change content of the initial functions.
import json
import xml.etree.ElementTree as ET
from argparse import ArgumentParser
from typing import Optional, Sequence

import requests


class UnhandledException(Exception):
    pass


def rss_parser(
        xml: str,
        limit: Optional[int] = None,
):

    try:
        response = requests.get(xml)
        response.raise_for_status()
        xml_data = response.text
        root = ET.fromstring(xml_data)

        channel = root.find('channel')
        items = channel.findall('.//item')

        parsed_data = {
            'title': channel.findtext('title'),
            'link': channel.findtext('link'),
            'lastBuildDate': channel.findtext('lastBuildDate'),
            'pubDate': channel.findtext('pubDate'),
            'language': channel.findtext('language'),
            'categories': [category.text for category in channel.findall('.//category')],
            'managingEditor': channel.findtext('managingEditor'),
            'description': channel.findtext('description'),
            'items': []
        }

        for item in items:
            item_data = {
                'title': item.findtext('title'),
                'author': item.findtext('author'),
                'pubDate': item.findtext('pubDate'),
                'link': item.findtext('link'),
                'category': item.findtext('category'),
                'description': item.findtext('description')
            }
            parsed_data['items'].append(item_data)

            if limit and len(parsed_data['items']) >= limit:
                break

        return parsed_data
    except requests.exceptions.RequestException as request_error:
        print(f"An error occurred while requesting the URL: {request_error}")
        return {}
    except ET.ParseError as parse_error:
        print(f"An error occurred while parsing XML: {parse_error}")
        return {}
    except Exception as e:
        print(f"An unexpected error 'rss_parser' func occurred: {e}")
        return {}


def main(argv: Optional[Sequence] = None):
    """
    The main function of your task.
    """
    parser = ArgumentParser(
        prog="rss_reader",
        description="Pure Python command-line RSS reader.",
    )
    parser.add_argument("source", help="RSS URL", type=str, nargs="?")
    parser.add_argument(
        "--json", help="Print result as JSON in stdout", action="store_true"
    )
    parser.add_argument(
        "--limit", help="Limit news topics if this parameter provided", type=int
    )

    args = parser.parse_args(argv)

    parsed_data = rss_parser(args.source, args.limit)

    if args.json:
        try:
            print(json.dumps(parsed_data, indent=2, ensure_ascii=False))
        except (TypeError, ValueError, OverflowError) as e:
            print(f"An error occurred while serializing to JSON: {e}")
    else:
        try:
            print(f"Feed: {parsed_data.get('title')}")
            print(f"Link: {parsed_data.get('link')}")
            print(f"Last Build Date: {parsed_data.get('lastBuildDate')}")
            print(f"Publish Date: {parsed_data.get('pubDate')}")
            print(f"Language: {parsed_data.get('language')}")
            categories = parsed_data.get('categories', [])
            categories_str = " ".join(categories)
            print(f"Categories: {categories_str}")
            print(f"Editor: {parsed_data.get('managingEditor')}")
            print(f"Description: {parsed_data.get('description')}\n")

            for item in parsed_data.get('items'):
                print(f"Title: {item.get('title')}")
                print(f"Author: {item.get('author')}")
                print(f"Published: {item.get('pubDate')}")
                print(f"Link: {item.get('link')}")
                print(f"Category: {item.get('category')}\n")
                print(f"{item.get('description')}\n")
            return 0
        except Exception as e:
            raise UnhandledException(e)


if __name__ == "__main__":
    main()
