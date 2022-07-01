import httpx
import argparse
import hashlib
import time

from bs4 import BeautifulSoup


def get_hash(s):
    return hashlib.sha256(s.encode()).hexdigest()


def get_content(site, selector):
    resp = httpx.get(site)
    out = resp.text

    if selector is not None:
        soup = BeautifulSoup(out, 'html.parser')
        targets = soup.select(selector)

        out = "\n".join([str(t) for t in targets])

    checksum = get_hash(out)
    content = (out, checksum)

    return content


def main(site=None, selector=None, frequency=None, ntfy_channel=None):
    content = None
    succesive_errors = 0

    while True:
        next_content = None
        try:
            next_content = get_content(site, selector)
        except Exception as e:
            payload = f"Siteeagle for '{site}' had an error."
            if succesive_errors >= 3:
                payload = f"[TERMINATING!] {payload}"

            httpx.post(f"https://ntfy.sh/{ntfy_channel}",
                       data=payload)

            if succesive_errors >= 3:
                raise e

            succesive_errors += 1
            time.sleep(frequency)
            continue

        if content is not None:
            if content[1] != next_content[1]:
                payload = f"Site ({site}) change from '{content[0]}' to '{next_content[0]}'"

                httpx.post(f"https://ntfy.sh/{ntfy_channel}", data=payload)

        content = next_content
        succesive_errors = 0

        time.sleep(frequency)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--site", type=str,
                        help="location of site to monitor")
    parser.add_argument("-z", "--selector", type=str,
                        help="selector to watch for the given site")
    parser.add_argument("-f", "--frequency", type=int, default=30,
                        help="amount of seconds to wait until next retry")
    parser.add_argument("-c", "--ntfy-channel", type=str,
                        help="the channel topic to use for ntfy.sh")

    args = vars(parser.parse_args())

    main(**args)
