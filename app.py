import argparse
import asyncio
import logging
import pathlib
import re
import sys
from typing import IO

import aiofiles
import aiohttp
from aiohttp import ClientSession

OUTPUT_FILE = "found_matches.txt"
logging.basicConfig(
    filename=OUTPUT_FILE,
    filemode='a',
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("areq")
logging.getLogger("chardet.charsetprober").disabled = True

"""Read URLs from input CLI argument asynchronously"""


async def fetch_html_content(url: str, session: ClientSession, **kwargs) -> str:
    resp = await session.request(method="GET", url=url, **kwargs)
    resp.raise_for_status()
    logger.info("Got response [%s] for URL: %s", resp.status, url)
    html_content = await resp.text()
    return html_content


async def find_regex(url: str, regs: set, session: ClientSession, **kwargs) -> list:
    unique_matches = set()
    result = []

    try:
        html_content = await fetch_html_content(url=url, session=session, **kwargs)
    except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,

    ) as e:
        logger.error(
            "aiohttp exception for %s [%s]: %s",
            url,
            getattr(e, "status", None),
            getattr(e, "message", None),
        )

        result.append([regs, str(e)])
        return result
    except Exception as e:
        logger.exception(
            "Non-aiohttp exception occured:  %s", getattr(e, "__dict__", {})
        )
        result.append([regs, str(e)])
        return result
    else:
        for reg in regs:
            for match in re.findall(reg, html_content):
                unique_matches.add(match)
        result.append([regs, unique_matches])

        logger.info("Found %d matches for %s", len(unique_matches), url)
        return result


"""Write single matching result asynchronously"""


async def write_matching_res(file: IO, url: str, regs: set, **kwargs) -> None:
    response = await find_regex(url=url, regs=regs, **kwargs)
    if not response:
        return None
    async with aiofiles.open(file, "a", encoding="utf-8") as f:
        for resp in response:
            await f.write(f"{url}\t{resp}\n")


"""Write concurrently to output file the regex matching results for multiple input URLs"""


async def write_regex_matches(file: IO, urls, regs, **kwargs) -> None:
    async with ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(
                write_matching_res(file=file, url=url, regs=regs, session=session, **kwargs)
            )
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    assert sys.version_info >= (3, 6), "Script requires Python 3.6+."
    current_dir = pathlib.Path(__file__).parent
    output_path = current_dir.joinpath(OUTPUT_FILE)

    with open(output_path, "w") as outfile:
        outfile.write("initial_url\tregex_matching_result\n")

    """Parse input arguments for CLi script:"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--urls", required=True, help="URLs", nargs='+', default=[])  # urls delimited by space
    parser.add_argument("--regex", required=True, help="content regex", nargs='+',
                        default=[])  # regex delimited by space
    args = vars(parser.parse_args())

    input_urls = args['urls']
    input_regs = args['regex']

    """Asynchronously find & write regex matches for URL:"""
    asyncio.run(write_regex_matches(file=output_path, urls=set(input_urls), regs=set(input_regs)))
