from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import re
import time

def extract_video_id(url):
    # Define the patterns for extracting video IDs
    patterns = [
        r"youtu\.be\/([^#\&\?]{11})",  # youtu.be/<id>
        r"\?v=([^#\&\?]{11})",         # ?v=<id>
        r"\&v=([^#\&\?]{11})",         # &v=<id>
        r"embed\/([^#\&\?]{11})",      # embed/<id>
        r"\/v\/([^#\&\?]{11})"         # /v/<id>
    ]

    # Compile the patterns into regular expressions
    compiled_patterns = [re.compile(pattern) for pattern in patterns]

    # Try to extract the video ID using the patterns
    for pattern in compiled_patterns:
        match = pattern.search(url)
        if match:
            return match.group(1)

    return None

# Set up Chrome options for headless browsing
chrome_options = Options()
chrome_options.add_argument("--headless")  # Enable headless mode
chrome_options.add_argument("--disable-gpu")  # Disable GPU usage

# Create a new Chrome WebDriver instance with headless options
driver = webdriver.Chrome(options=chrome_options)

# Open the text file containing search terms
with open("search-terms.txt", "r") as file:
    search_terms = file.read().splitlines()

# Open the CSV file in append mode
with open("video_ids.csv", "a", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)

    # Iterate through the search terms
    for query in search_terms:
        print(f"Searching for: {query}")

        # Construct the YouTube search URL
        search_url = f"https://www.youtube.com/results?search_query={query}"

        # Navigate to the search URL using the headless browser
        driver.get(search_url)

        # Scroll down the page to load more results
        last_height = driver.execute_script("return document.documentElement.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)  # Wait for the page to load
            new_height = driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Get the page source after the browser has rendered the page
        page_source = driver.page_source

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(page_source, "html.parser")

        # Find all the video links in the search results
        video_links = soup.find_all("a", href=True)

        # Extract video IDs and titles from the video links
        for link in video_links:
            href = link["href"]

            # Extract the video ID using the separate function
            video_id = extract_video_id(href)

            if video_id:
                # Write the video ID and title to the CSV file
                writer.writerow([video_id, query])

# Quit the WebDriver instance
driver.quit()