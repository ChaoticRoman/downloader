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


def download_file(url, chunk_size=1024):
    local_filename = url.split('/')[-1]
    with get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk:
                f.write(chunk)
    return local_filename


if __name__ == "__main__":
    TEST_URL = (
        "https://raw.githubusercontent.com/ChaoticRoman/ChaoticRoman/main/README.md"
    )
    result = get(TEST_URL)
    print(result.status_code, result.content)

    fn = download_file(TEST_URL)
    import os
    os.system(f"ls {fn} && cat {fn} && rm {fn}")
