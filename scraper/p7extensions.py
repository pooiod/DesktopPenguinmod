import requests
import json

def get_download_urls():
    """
    Fetches folder names from a GitHub repository, checks for specific files on
    a different domain, and returns a JSON array of valid URLs.
    """
    github_api_url = "https://api.github.com/repos/pooiod/ScratchExtensions/contents/ext"
    download_url_base = "https://p7scratchextensions.pages.dev/ext/"

    downloadable_urls = []

    try:
        response = requests.get(github_api_url)
        response.raise_for_status()
        ext_contents = response.json()

        for item in ext_contents:
            if item['type'] == 'dir':
                folder_name = item['name']
                
                main_js_url = f"{download_url_base}{folder_name}/main.js"
                dev_js_url = f"{download_url_base}{folder_name}/dev.js"

                try:
                    response_main = requests.get(main_js_url, timeout=5)
                    if response_main.status_code == 200 and "62478319" not in response_main.text:
                        downloadable_urls.append(main_js_url)
                except requests.RequestException:
                    pass

                try:
                    response_dev = requests.get(dev_js_url, timeout=5)
                    if response_dev.status_code == 200 and "62478319" not in response_dev.text:
                        downloadable_urls.append(dev_js_url)
                except requests.RequestException:
                    pass

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return json.dumps({"error": str(e)})

    return json.dumps(downloadable_urls, indent=2)

if __name__ == "__main__":
    urls_json = get_download_urls()
    print(urls_json)
