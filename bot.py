import os
import json
import random
import hrequests
import threading
from time import sleep
from urllib.parse import urlparse
from datetime import datetime

# Load configuration from config.json
project_path = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(project_path, "config.json")

# Load configuration
with open(config_path, 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

# Configuration variables
website_url = config.get("website_url", "https://example.com")
proxy = config.get("proxy", "")
number_of_threads = config.get("number_of_threads", 3)
scroll_movements = config.get("scroll_movements", 5)
external_queries = config.get("external_queries", [])

# Load words for random queries
with open(os.path.join(project_path, "words.json"), 'r', encoding='utf-8') as file:
    words = json.load(file)

class ImpressionBot:
    """
    A bot that simulates human-like browsing behavior to generate website impressions.
    """
    def __init__(self, tag):
        """
        Initialize the bot with a unique tag for identification.
        
        Args:
            tag (int): Unique identifier for the bot instance
        """
        self.tag = tag
        # Initialize browser session with random browser type
        self.webpage = hrequests.BrowserSession(
            mock_human=True,
            headless=True,
            browser=random.choice(["chrome", "firefox"]),
            proxy=proxy
        )

    def launch_browser(self):
        """
        Launch the browser session and perform the browsing simulation.
        """
        try:
            # Set random referer header
            self.webpage.setHeaders({
                "Referer": f"{random.choice(external_queries)}{random.choice(words)}"
            })
            # Navigate to target website
            self.webpage.goto(website_url)
            self.webpage.awaitNavigation(timeout=120.0)
            # Perform random crawling
            self.random_crawl()
            self.webpage.close()
        except Exception as e:
            log(f"Error in session {self.tag}: {str(e)}")
            self.webpage.close()
    
    def get_domain_name(self, url: str) -> str:
        """
        Extract domain name from URL.
        
        Args:
            url (str): URL to extract domain from
            
        Returns:
            str: Domain name
        """
        return urlparse(url).netloc
    
    def random_crawl(self):
        """
        Perform random crawling behavior within the website.
        """
        log(f"Crawling {self.webpage.url} on session {self.tag}")
        i = 0
        max_page_deep = random.choice(range(1, 5))
        
        while i < max_page_deep:
            try:
                self.random_scroll()
                all_links = self.webpage.html.find_all('a')
                
                if len(all_links) > 0:
                    random_link = list(all_links[random.randint(0, len(all_links)-1)].absolute_links)[0]
                    if self.get_domain_name(random_link) == self.get_domain_name(self.webpage.url):
                        log(f"Opening {random_link} on {self.tag}")
                        self.webpage.goto(random_link)
                        self.webpage.awaitNavigation()
                        sleep(random.uniform(1, 10))
                else:
                    break
            except Exception as e:
                log(f"Error during crawling in session {self.tag}: {str(e)}")
            i += 1
            
        # Navigate to external site
        self.webpage.goto(f"{random.choice(external_queries)}{random.choice(words)}")
        self.webpage.awaitNavigation()
        sleep(random.uniform(1, 10))
        self.random_scroll()

    def random_scroll(self):
        """
        Simulate human-like scrolling behavior.
        """
        i = 0
        page_height = self.webpage.evaluate("document.body.scrollHeight")
        
        while i < scroll_movements:
            try:
                current_scroll_y = self.webpage.evaluate("window.scrollY")
                random_scroll_distance = random.randint(500, 1000)
                
                if random.choice(['up', 'down']) == 'up':
                    random_scroll_distance = -random.randint(100, 500)
                    
                new_scroll_y = min(
                    current_scroll_y + random_scroll_distance,
                    page_height - self.webpage.evaluate("window.innerHeight")
                )
                
                self.webpage.evaluate(f"""
                    window.scrollBy({{
                        top: {new_scroll_y - current_scroll_y}, 
                        left: 0, 
                        behavior: 'smooth'
                    }});
                """)
                sleep(random.uniform(1, 10))
            except Exception as e:
                log(f"Error during scrolling in session {self.tag}: {str(e)}")
            i += 1

def spawn_bot(tag):
    """
    Spawn a new bot instance with the given tag.
    
    Args:
        tag (int): Unique identifier for the bot instance
    """
    log(f"Starting session: {tag}")
    bot = ImpressionBot(tag)
    bot.launch_browser()
    log(f"Completed session: {tag}")

def log(*msg):
    """
    Log messages to both console and log file.
    
    Args:
        *msg: Variable number of message arguments
    """
    with open(os.path.join(project_path, "log.txt"), 'a', encoding="utf-8") as log_file:
        log_file.write('[{:%d/%m/%Y - %H:%M:%S}] {}\n'.format(datetime.now(), *msg))
    print('[{:%d/%m/%Y - %H:%M:%S}] {}'.format(datetime.now(), *msg))

if __name__ == '__main__':
    log("Starting Website Impression Bot Engine")
    tag = 0
    while True:
        try:
            threads = []
            for _ in range(number_of_threads):
                tag += 1
                thread = threading.Thread(target=spawn_bot, args=(tag,))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()
            log("Batch Completed")
        except Exception as e:
            log("Error in main loop")
            log(str(e))