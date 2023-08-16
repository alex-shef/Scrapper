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

        fields_channel = ['title',
                          'link',
                          'lastBuildDate',
                          'pubDate',
                          'language',
                          './/category',
                          'managingEditor',
                          'description']
        fields_item = ['title',
                       'author',
                       'pubDate',
                       'link',
                       'category',
                       'description']

        parsed_data = dict()
        for elem in fields_channel:
            if elem == './/category':
                categories = []
                for category in channel.findall('.//category'):
                    category_text = category.text
                    if category_text not in categories:
                        categories.append(category_text)
                if categories:
                    parsed_data['categories'] = categories
            else:
                if channel.findtext(elem):
                    parsed_data[elem] = channel.findtext(elem)

        item_data = dict()
        for item in items:
            if parsed_data.get('items') is None:
                parsed_data['items'] = []
            item_data.clear()
            for elem in fields_item:
                if item.findtext(elem):
                    item_data[elem] = item.findtext(elem)
            if item_data:
                parsed_data['items'].append(item_data)

            if limit and len(parsed_data['items']) >= limit:
                break

        if json:
            return [json_module.dumps(parsed_data, indent=2, ensure_ascii=False)]
        else:
            output = []
            if parsed_data.get('title'):
                output.append(f"Feed: {parsed_data.get('title')}")
            if parsed_data.get('link'):
                output.append(f"Link: {parsed_data.get('link')}")
            if parsed_data.get('lastBuildDate'):
                output.append(f"Last Build Date: {parsed_data.get('lastBuildDate')}")
            if parsed_data.get('pubDate'):
                output.append(f"Publish Date: {parsed_data.get('pubDate')}")
            if parsed_data.get('language'):
                output.append(f"Language: {parsed_data.get('language')}")
            categories = parsed_data.get('categories', [])
            if categories:
                categories_str = " ".join(categories)
                output.append(f"Categories: {categories_str}")
            if parsed_data.get('managingEditor'):
                output.append(f"Editor: {parsed_data.get('managingEditor')}")
            if parsed_data.get('description'):
                output.append(f"Description: {parsed_data.get('description')}\n")

            if parsed_data.get('items'):
                for item in parsed_data.get('items'):
                    if item.get('title'):
                        output.append(f"Title: {item.get('title')}")
                    if item.get('author'):
                        output.append(f"Author: {item.get('author')}")
                    if item.get('pubDate'):
                        output.append(f"Published: {item.get('pubDate')}")
                    if item.get('link'):
                        output.append(f"Link: {item.get('link')}")
                    if item.get('category'):
                        output.append(f"Category: {item.get('category')}")
                    output.append("")
                    if item.get('description'):
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
