"""
Main script to scrape the comments of any YouTube video.

Example:
    $ python main.py YOUTUBE_VIDEO_URL
"""

import csv
import io
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import sys
import time

def scrape(url):
    """
    Extracts the comments from the YouTube video given by the URL.

    Args:
        url (str): The URL to the YouTube video

    Raises:
        selenium.common.exceptions.NoSuchElementException:
        When certain elements to look for cannot be found
    """

    # Use ChromeDriverManager to handle the driver installation
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Navigate to the URL, maximize the current window, and
    # then suspend execution for (at least) 5 seconds (this
    # gives time for the page to load).
    driver.get(url)
    driver.maximize_window()
    time.sleep(5)

    try:
        # Extract the elements storing the video title and
        # comment section.
        title = driver.find_element("xpath", '//*[@id="container"]/h1/yt-formatted-string').text
        comment_section = driver.find_element("xpath", '//*[@id="comments"]')
    except exceptions.NoSuchElementException:
        # Note: YouTube may have changed their HTML layouts for
        # videos, so raise an error for sanity's sake in case the
        # elements provided cannot be found anymore.
        error = "Error: Double check selector OR "
        error += "element may not yet be on the screen at the time of the find operation"
        print(error)
        driver.quit()
        return

    # Scroll into view the comment section, then allow some time
    # for everything to be loaded as necessary.
    driver.execute_script("arguments[0].scrollIntoView();", comment_section)
    time.sleep(7)

    # Scroll all the way down to the bottom in order to get all the
    # elements loaded (since YouTube dynamically loads them).
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while True:
        # Scroll down 'til "next load".
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

        # Wait to load everything thus far.
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # One last scroll just in case.
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

    try:
        # Extract the elements storing the usernames and comments.
        username_elems = driver.find_elements("xpath", '//*[@id="author-text"]')
        comment_elems = driver.find_elements("xpath", '//*[@id="content-text"]')
    except exceptions.NoSuchElementException:
        error = "Error: Double check selector OR "
        error += "element may not yet be on the screen at the time of the find operation"
        print(error)
        driver.quit()
        return

    print("> VIDEO TITLE: " + title + "\n")

    with io.open('results.csv', 'w', newline='', encoding="utf-16") as file:
        writer = csv.writer(file, delimiter=",", quoting=csv.QUOTE_ALL)
        writer.writerow(["Username", "Comment"])
        for username, comment in zip(username_elems, comment_elems):
            writer.writerow([username.text, comment.text])

    driver.quit()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        scrape(sys.argv[1])
    else:
        print("Usage: python main.py YOUTUBE_VIDEO_URL")
