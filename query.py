from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
import urllib
import time

driver = webdriver.Firefox(service=Service(executable_path=GeckoDriverManager().install()))

# TODO
#   get_audio_file()
#   get_stage_files()

PAUSE_TIME = 1.0
WHITELISTED_CHANNELS = [    
    "Mnet",
    "SBSKPOPPLAY",
    "kbsworldtv",
    "MBCkpop",
    "THEKPOP",
    "KBSKPOP",
    "ALLTHEKPOP",
]
BLACKLISTED_TERMS = [
    "stage mix",
    "fan cam",
    "fancam",
    "full cam",
    "focus",
    "clip",
    "one take",
    "karaoke"
]

def close_driver():
    """Closes the WebDriver"""
    return driver.quit()

def is_reel(element) -> bool:
    """Check if web element is a YouTube reel
    
    Args:
        element (HTMLelement): element from WebDriver

    Returns:
        bool: is element a YouTube reel?
    """
    if 'ytd-reel-item-renderer' in element.get_attribute('class').split():
        return True
    return False

def scroll_driver(pause_time: float):
    """Scrolls the Selenium WebDriver's current page

    Args:
        pause_time (float): Time to wait for page to load content
    """
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # scroll the driver to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # wait for content to load
        time.sleep(pause_time)

        # compare new scroll height with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def check_title(title: str, artist: str) -> bool:
    """Validates stages by checking title for keywords

    Args:
        title (str): title of the video
        artist (str): artist of the song

    Returns:
        bool: is the video a valid stage?
    """
    # TODO:
    #   come up with better way to filter videos based on titles
    for term in BLACKLISTED_TERMS:
        if term in title.lower() or not artist in title.lower():
            return False
    return True

def search_videos(artist: str, song: str) -> [str]:
    """Searches YouTube for stage performances

    Args:
        artist (str): artist of the song
        song (str): title of the song
    
    Returns:
        video_urls (list): a list of video url strings
    """
    driver.get(f"https://www.youtube.com/results?search_query={artist}+{song}+stage")
    scroll_driver(PAUSE_TIME)
    r = driver.page_source

    # find video content container
    elements = driver.find_elements(By.XPATH,'//*[@id="dismissible"]')

    video_urls = []

    for e in elements:
        if is_reel(e):
            continue

        title = e.find_element(By.XPATH,'.//*[@id="video-title"]').text
        channel_info = e.find_element(By.XPATH,'.//*[@id="channel-info"]')
        channel_path = channel_info.find_element(By.TAG_NAME,'a').get_attribute('href')
        channel_name = urllib.parse.urlparse(channel_path).path.split('/')[-1]
        url = e.find_element(By.TAG_NAME,'a').get_attribute('href')
        
        print(f"CHANNEL: {channel_name}")
        print(f"URL: {url}")

        if channel_name in WHITELISTED_CHANNELS and check_title(title, artist):
            video_urls.append(url)
    return video_urls

def search_audio(artist: str , song: str) -> str:
    """Searches YouTube for a lyric video

    Args:
        artist (str): artist of the song
        song (str): title of the song

    Returns:
        audio_url (str): video url string
    """
    driver.get(f"https://www.youtube.com/results?search_query={artist}+{song}+lyrics")
    r = driver.page_source

    #find video content container
    element = driver.find_element(By.XPATH, '//*[@id="dismissible"]')
    audio_url = element.find_element(By.TAG_NAME,'a').get_attribute('href')
    return audio_url

def url_to_id(url):
    """Extracts id from YouTube video url
    
    Args:
        url (str): video url string
    
    Returns:
        vid_id (str): id slug
    """
    url_data = urllib.parse.urlparse(url)
    split_url = urllib.parse.parse_qs(url_data.query)
    vid_id = split_url['v'][0]
    return vid_id

def close_driver():
    """Closes the WebDriver"""
    return driver.quit()