import unittest
from player_scraper.scraper import Scraper
import time
from selenium.webdriver.common.by import By

class TestScraper(unittest.TestCase):
    def setUp(self):
        self.bot = Scraper("https://www.premierleague.com/stats/top/players/goals?se=418")
    
    def test_accept_cookies(self):
        self.bot.accept_cookies(xpath='//button[@class="_2hTJ5th4dIYlveipSEMYHH BfdVlAo_cgSVjDUegen0F js-accept-all-close"]')
        self.bot.driver.find_element(By.XPATH, '//button[@class="_2hTJ5th4dIYlveipSEMYHH BfdVlAo_cgSVjDUegen0F js-accept-all-close"]')
    
    def test_scroll_page(self):
        self.bot.scroll_page(self, x=0, y=300)
        self.bot.driver.execute_script(f'window.scrollBy({x},{y})')

    def test_player_data_list(self):
        self.bot.player_data_list()
        time.sleep(2)
        actual_value = self.bot.driver.current_url
        print(actual_value)
        expected_value = "https://www.premierleague.com/stats/top/players/goals?se=418"
        self.assertEqual(actual_value, expected_value)

    def test_player_links_uuid_data(self):
        self.bot.player_links_uuid("https://www.premierleague.com/players/5178/player/overview")
        time.sleep(2)
        actual_value = self.bot.driver.current_url
        expected_value = "https://www.premierleague.com/players/5178/player/overview"
        self.assertEqual(actual_value, expected_value)
    
    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main(verbosity=2)