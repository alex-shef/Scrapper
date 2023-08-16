# You shouldn't change  name of function or their arguments,
# but you can change content of the initial functions.
import json as json_module
import xml.etree.ElementTree as ET
from argparse import ArgumentParser
from typing import List, Optional, Sequence

import requests


class UnhandledException(Exception):
    pass


def rss_parser(
    xml: str,
    limit: Optional[int] = None,
    json: bool = False,
) -> List[str]:
    """
    RSS parser.

    Args:
        xml: XML document as a string.
        limit: Number of the news to return. if None, returns all news.
        json: If True, format output as JSON.

    Returns:
        List of strings.
        Which then can be printed to stdout or written to file as a separate lines.

    Examples:
        # >>> xml = '<rss><channel><title>Some RSS Channel</title><link>https://some.rss.com</link><description>Some RSS Channel</description></channel></rss>'
        # >>> rss_parser(xml)
        ["Feed: Some RSS Channel",
        "Link: https://some.rss.com"]
        # >>> print("\\n".join(rss_parser(xml)))
        Feed: Some RSS Channel
        Link: https://some.rss.com
    """
    try:
        root = ET.fromstring(xml)

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

        if json:
            return [json_module.dumps(parsed_data, indent=2, ensure_ascii=False)]
        else:
            output = []
            output.append(f"Feed: {parsed_data['title']}")
            output.append(f"Link: {parsed_data['link']}")
            output.append(f"Last Build Date: {parsed_data['lastBuildDate']}")
            output.append(f"Publish Date: {parsed_data['pubDate']}")
            output.append(f"Language: {parsed_data['language']}")
            categories = parsed_data.get('categories', [])
            categories_str = " ".join(categories)
            output.append(f"Categories: {categories_str}")
            output.append(f"Editor: {parsed_data.get('managingEditor')}")
            output.append(f"Description: {parsed_data['description']}\n")

            for item in parsed_data.get('items'):
                output.append(f"Title: {item.get('title')}")
                output.append(f"Author: {item.get('author')}")
                output.append(f"Published: {item.get('pubDate')}")
                output.append(f"Link: {item.get('link')}")
                output.append(f"Category: {item.get('category')}\n")
                output.append(f"{item.get('description')}\n")

            return output

    except ET.ParseError as parse_error:
        error_message = f"An error occurred while parsing XML: {parse_error}"
    except Exception as e:
        error_message = f"An unexpected error occurred in 'rss_parser' func: {e}"

    return [error_message]

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
    xml = requests.get(args.source).text
    try:
        print("\n".join(rss_parser(xml, args.limit, args.json)))
        return 0
    except Exception as e:
        raise UnhandledException(e)


if __name__ == "__main__":
    main()
