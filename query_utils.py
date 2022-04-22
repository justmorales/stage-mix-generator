from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
import urllib
import time
driver = webdriver.Firefox(service=Service(executable_path=GeckoDriverManager().install()))

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

def scroll_driver():
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # scroll the driver to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # wait for content to load
        time.sleep(PAUSE_TIME)

        # compare new scroll height with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def check_title(title, artist):
    # TODO:
    ## come up with better way to filter videos based on titles
    for term in BLACKLISTED_TERMS:
        if term in title.lower() or not artist in title.lower():
            return False
    return True

class QueryObject:
    def __init__(self, song, artist):
        self.audio_url = ""
        self.video_urls = []
        self.song = song
        self.artist = artist
        self.audio_query = f"{artist} {song} lyrics"
        self.video_query = f"{artist} {song} stage"
    
    def search_video(self):
        driver.get(f"https://www.youtube.com/results?search_query={self.video_query}")
        scroll_driver()
        r = driver.page_source

        # find video content container
        elements = driver.find_elements(By.XPATH,'//*[@id="dismissible"]')

        for e in elements:
            title = e.find_element(By.XPATH,'.//*[@id="video-title"]').text
            channel_info = e.find_element(By.XPATH,'.//*[@id="channel-info"]')
            channel_path = channel_info.find_element(By.TAG_NAME,'a').get_attribute('href')
            channel_name = urllib.parse.urlparse(channel_path).path.split('/')[-1]
            url = e.find_element(By.TAG_NAME,'a').get_attribute('href')
            
            print(f"CHANNEL: {channel_name}")
            print(f"URL: {url}")

            if channel_name in WHITELISTED_CHANNELS and check_title(title, self.artist):
                self.video_urls.append(url)
        return self.video_urls
    
    # defined as separate function from search_video because it doesn't need to scroll
    # maybe combine the two functions later on
    def search_audio(self):
        driver.get(f"https://www.youtube.com/results?search_query={self.audio_query}")
        r = driver.page_source

        #find video content container
        element = driver.find_element(By.XPATH, '//*[@id="dismissible"]')
        self.audio_url = element.find_element(By.TAG_NAME,'a').get_attribute('href')
        return self.audio_url
    
    # idk how python's garbage collection works
    # just safety against memory leaks when i do headless queries
    def closeDriver(self):
        driver.quit()