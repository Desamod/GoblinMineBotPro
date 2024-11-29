import requests
import re

from bs4 import BeautifulSoup

from bot.core.headers import headers
from bot.utils import logger
from bot.utils.graphql import Query

base_api_url = 'https://api.goblinmine.game'
endpoints = ['/graphql']

ws_api_url = 'ws.goblinmine.game'
ws_key = 'h2co7fdfjnsiwzdrapmq'
app_hash = '4aaa79c6-3498-4441-ae94-f3fb45781588'


def find_js_files(base_url):
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        content = response.text
        soup = BeautifulSoup(content, 'html.parser')
        scripts = soup.find_all('script', src=True)
        app_js_file = None
        chunk_js_files = re.findall(r'src="(/_next/static/chunks/\d+-[a-f0-9]+\.js)"', content)
        for script in scripts:
            if '/app/(web)/layout' in script.attrs.get('src'):
                app_js_file = script['src']

        chunk_js_files = list(reversed(chunk_js_files))
        return app_js_file, chunk_js_files
    except requests.RequestException as e:
        logger.warning(f"Error fetching the base URL: {e}")
        return None, None


def get_js_content(js_url):
    try:
        response = requests.get(js_url)
        response.raise_for_status()
        content = response.text
        match = re.findall(r'"(https?://[^"]+)"', content)
        if match:
            return match, content
        else:
            logger.info("Could not find urls in the content.")
            return None
    except requests.RequestException as e:
        logger.warning(f"Error fetching the JS file: {e}")
        return None


def extract_queries_and_fragments(content):
    result = []
    current = ''
    depth = 0
    extra_chars = 0
    i = 0
    while i < len(content):
        char = content[i]
        if depth == 0 and char != '{' and char != '}':
            extra_chars += 1
        if char == '{' and depth == 0:
            start = i
            depth += 1
            i += 1
            continue

        elif char == '}' and depth == 1:
            result.append(content[start - extra_chars:i + 1])
            depth = 0
            extra_chars = 0
            i += 1
            continue

        elif char == '{':
            depth += 1
            i += 1
            continue
        elif char == '}':
            depth -= 1
            i += 1
            continue
        else:
            i += 1
    return result


def is_valid_endpoints():
    base_url = headers['Origin']
    app_js_file, chunk_js_files = find_js_files(base_url)

    if chunk_js_files:
        is_graphql = False
        graphql_content = ''
        for chunk_js in chunk_js_files:
            if is_graphql:
                break
            try:
                response = requests.get(f"{base_url}{chunk_js}")
                response.raise_for_status()
                content = response.text
                content = content.replace('\\n', '')
                content = ''.join(content.split())
                for query_data in Query:
                    data = query_data.replace('__typename', '')
                    data = ''.join(data.split())
                    if data in content:
                        is_graphql = True
                        graphql_content = content
                        break
            except requests.RequestException as e:
                logger.warning(f"Error getting the graphql JS file: {e}")
                return None

        if is_graphql:
            for query_data in Query:
                data = query_data.replace('__typename', '')
                data = ''.join(data.split())
                matches = extract_queries_and_fragments(data)
                for match in matches:
                    if match not in graphql_content:
                        logger.info(f"Graphql data <y>{match}</y> not found in JS code")
                        return False
        else:
            logger.warning(f"Graphql query JS not found")
            return False
    else:
        logger.warning(f"Graphql queries not found")
        return False

    if app_js_file:
        full_url = f"{base_url}{app_js_file}"
        result, content = get_js_content(full_url)
        if not result:
            logger.warning(f"Js code has changed! {full_url}")
            return False
        if base_api_url not in result:
            logger.warning(f"Base URL <lc>{base_api_url}</lc> not found.")
            return False

        for endpoint in endpoints:
            endpoint_mask = f'("{base_api_url}","{endpoint}")'
            if endpoint_mask not in content:
                logger.warning(f"Endpoint <lc>{endpoint}</lc> not found.")
                return False

        if ws_api_url not in content:
            logger.warning(f"WS <lc>{ws_api_url}</lc> not found.")
            return False

        if ws_key not in content:
            logger.warning(f"WS key <lc>{ws_api_url}</lc> not found.")
            return False

        if app_hash not in content:
            matches = re.findall(r'"App-B":"(.*?)"', content)
            if len(matches) == 0:
                logger.warning(f"APP hash <lc>{app_hash}</lc> not found.")
                return False
            else:
                logger.warning(f"APP hash <lc>{app_hash}</lc> has changed.")
                headers['App-B'] = matches[0]
                logger.success(f"APP hash automatically changed to <lc>{matches[0]}</lc>")
        else:
            headers['App-B'] = app_hash
        return True
    else:
        logger.warning("Could not find any main.js format. Dumping page content for inspection:")
        try:
            response = requests.get(base_url)
            print(response.text[:1000])
            return False
        except requests.RequestException as e:
            logger.warning(f"Error fetching the base URL for content dump: {e}")
            return False
