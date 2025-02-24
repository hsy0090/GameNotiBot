import feedparser
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import requests

import asyncio
from pyppeteer import launch

import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def get_steamdb_free_games():
    """Fetch free games from Steam using Steam API."""
    url_apps = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    free_games = []

    try:
        # Fetch all Steam apps
        response = requests.get(url_apps)
        if response.status_code != 200:
            print(f"Failed to fetch Steam app list: {response.status_code}")
            return []

        apps = response.json().get("applist", {}).get("apps", [])

        # Debugging: Print the number of apps retrieved
        print(f"Total apps retrieved from Steam API: {len(apps)}")

        # Check for free games (limit the loop to 100 apps for testing)
        for app in apps[:100]:  # Adjust or remove the limit as needed
            app_id = app["appid"]
            app_name = app.get("name", "Unknown")
            app_details_url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
            
            try:
                # Fetch app details
                app_details_response = requests.get(app_details_url)
                if app_details_response.status_code != 200:
                    print(f"Failed to fetch details for app {app_name} (ID: {app_id}): {app_details_response.status_code}")
                    continue

                data = app_details_response.json().get(str(app_id), {}).get("data", {})
                if data.get("is_free"):  # Check if the app is free
                    description = data.get("short_description", "No description available")
                    url = f"https://store.steampowered.com/app/{app_id}"

                    free_games.append({
                        "title": app_name,
                        "description": description,
                        "url": url,
                    })

                    # Debugging: Log free game details
                    print(f"Found free game: {app_name} - {url}")
            except Exception as e:
                print(f"Error fetching details for app {app_name} (ID: {app_id}): {e}")
        
        if not free_games:
            print("No free games found in the current list.")

        return free_games
    except Exception as e:
        print(f"An error occurred while fetching Steam free games: {e}")
        return []
        
def get_epic_free_games():
    """Fetch free games from the Epic Games Store API."""
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            return []

        data = response.json()

        # Debugging: Print raw API response to check the structure
        print("Raw API Response:", data)
        
        games = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
        free_games = []

        now = datetime.now(timezone.utc)  # Current UTC time

        for game in games:
            title = game.get("title", "Unknown")
            price = game.get("price", {})
            discount_price = price.get("totalPrice", {}).get("discountPrice")
            
            # Debugging: Print the details of each game
            print(f"Checking game: {title} - Discount Price: {discount_price}")
            
            if discount_price == 0:  # Check for completely free game
                start_date = datetime.fromisoformat(game.get("effectiveDate").replace("Z", "+00:00"))
                description = game.get("description", "No description available")
                
                # Use productSlug for generating accurate URLs
                product_slug = game.get("productSlug")
                url = f"https://store.epicgames.com/en-US/p/{product_slug}" if product_slug else "No URL available"
                
                free_games.append({
                    "title": title,
                    "description": description,
                    "url": url,
                })
                print(f"Found free game: {title} - {url}")  # Debug log for free games

        if not free_games:
            print("No free games found in the current list.")
        
        return free_games
    except Exception as e:
        print(f"An error occurred while fetching Epic Games: {e}")
        return []
