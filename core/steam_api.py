import logging
import requests
import json
import os
import time
import sys
import subprocess
import tempfile

logger = logging.getLogger(__name__)

# --- Constants ---
CACHE_DIR = "api_cache"
CACHE_EXPIRATION_SECONDS = 86400  # 24 hours

def get_depot_info_from_api(app_id):
    """
    Fetches depot and app info for a given app_id using a multi-tiered approach.

    Returns:
        dict: A dictionary containing 'depots' and 'installdir'.
              Returns an empty dict on failure.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f"{app_id}_depot_details.json")

    if os.path.exists(cache_file):
        try:
            file_age = time.time() - os.path.getmtime(cache_file)
            if file_age < CACHE_EXPIRATION_SECONDS:
                logger.info(f"Loading app details for AppID: {app_id} from local cache.")
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Could not read cache file {cache_file}. Fetching fresh data. Error: {e}")

    logger.info(f"Attempting to fetch app info for AppID {app_id} using steam.client...")
    api_data = _fetch_with_steam_client(app_id)

    if not api_data or not api_data.get('depots'):
        logger.warning(f"steam.client method failed for AppID {app_id}. Falling back to public Web API.")
        api_data = _fetch_with_web_api(app_id)

    # --- MODIFICATION START ---
    # The block that saved the parsed data to the cache has been removed.
    # --- MODIFICATION END ---

    return api_data

def _fetch_with_steam_client(app_id):
    """
    Uses the steam.client library to get product info, including installdir.
    """
    try:
        from steam.client import SteamClient
    except ImportError:
        logger.warning("`steam[client]` package not found. Skipping steam.client fetch method.")
        return {}

    script_content = f'''
import json, sys
from steam.client import SteamClient
try:
    client = SteamClient()
    client.anonymous_login()
    if not client.logged_on:
        sys.stderr.write("Failed to anonymously login to Steam.\\n")
        sys.exit(1)
    result = client.get_product_info(apps=[{app_id}], timeout=30)
    client.logout()
    print(json.dumps(result))
except Exception as e:
    sys.stderr.write(f"An exception occurred: {{e}}\\n")
    sys.exit(1)
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
        temp_file.write(script_content)
        temp_script_path = temp_file.name

    api_data = {}
    raw_stdout = ""
    try:
        python_executable = sys.executable
        result = subprocess.run(
            [python_executable, temp_script_path],
            capture_output=True, text=True, timeout=120, check=False, encoding='utf-8'
        )
        raw_stdout = result.stdout.strip()

        if result.returncode != 0:
            logger.error(f"steam.client subprocess failed. Stderr: {result.stderr.strip()}")
            return {}

        data = json.loads(raw_stdout)
        app_data = data.get("apps", {}).get(str(app_id), {})
        
        depot_info = {}
        installdir = None
        game_name = None
        
        if app_data:
            installdir = app_data.get('config', {}).get('installdir')
            game_name = app_data.get('name') or app_data.get('common', {}).get('name')
            depots = app_data.get("depots", {})
            for depot_id, depot_data in depots.items():
                if not isinstance(depot_data, dict): continue
                config = depot_data.get('config', {})
                depot_info[depot_id] = {
                    'name': depot_data.get('name', f"Depot {depot_id}"),
                    'oslist': config.get('oslist'),
                    'language': config.get('language'),
                    'steamdeck': config.get('steamdeck') == '1'
                }
        
        api_data = {'depots': depot_info, 'installdir': installdir, 'game_name': game_name}
        
    except Exception as e:
        logger.error(f"An unexpected error occurred in _fetch_with_steam_client: {e}", exc_info=True)
    finally:
        os.unlink(temp_script_path)
        
    return api_data

def _fetch_with_web_api(app_id):
    """
    Fetches data from the public Steam store API as a fallback.
    """
    url = "https://store.steampowered.com/api/appdetails"
    params = {"appids": app_id}
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        return _parse_web_api_response(app_id, data)
    except requests.exceptions.RequestException as e:
        logger.error(f"Web API request failed for AppID {app_id}: {e}")
    return {}

def _parse_web_api_response(app_id, data):
    """
    Parses the JSON data from the public Web API.
    """
    depot_info = {}
    installdir = None
    game_name = None
    app_data_wrapper = data.get(str(app_id))

    if app_data_wrapper and app_data_wrapper.get("success"):
        app_data = app_data_wrapper.get("data", {})
        installdir = app_data.get("install_dir")
        game_name = app_data.get("name")
        depots = app_data.get("depots", {})
        for depot_id, depot_data in depots.items():
            if not isinstance(depot_data, dict): continue
            depot_info[depot_id] = {
                'name': depot_data.get('name', f"Depot {depot_id}"),
                'oslist': None, 'language': None, 'steamdeck': False
            }
            
    return {'depots': depot_info, 'installdir': installdir, 'game_name': game_name}
