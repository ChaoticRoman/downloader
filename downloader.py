import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()

DEFAULT_STATUSES_TO_RETRY_ON = [429, 500, 502, 503, 504]


def get(url, timeout=2.0, retries=3, backoff_factor=0.5, stream=False):
    """Optimized downloader with timeout, retries and backoff strategy.
    Based on: https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/
    """
    retry_strategy = Retry(total=retries, backoff_factor=backoff_factor,
        status_forcelist=DEFAULT_STATUSES_TO_RETRY_ON)
    adapter = HTTPAdapter(max_retries=retry_strategy)

    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)
    http.hooks["response"] = [assert_status_hook]

    return http.get(url, timeout=timeout, stream=stream)


def download(url, chunk_size=1024, destination_dir=None, filename=None):
    target = filename if filename else url.split('/')[-1]
    if destination_dir:
        target = os.path.join(destination_dir, target)
    with get(url, stream=True) as r:
        with open(target, 'wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
    return target


if __name__ == "__main__":
    TEST_URL = (
        "https://raw.githubusercontent.com/ChaoticRoman/ChaoticRoman/main/README.md"
    )
    result = get(TEST_URL)
    print(result.status_code, result.content)

    fn = download(TEST_URL)
    import os
    os.system(f"ls {fn} && cat {fn} && rm {fn}")
