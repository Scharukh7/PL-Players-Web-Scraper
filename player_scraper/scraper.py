#%%
import json
from pandas.io.json import json_normalize
import selenium
import requests
from bs4 import BeautifulSoup
import numpy as np
import urllib.request
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time     
import uuid
from uuid import UUID, uuid4
import os
import pandas as pd
from pandas import DataFrame
import boto3
import sqlalchemy
from sqlalchemy import create_engine
import shutil
from dotenv import load_dotenv
import yaml

class Scraper:
    """"
    this class is a scraper that can be used for browsing different websites - currently browsing premierleague website

    attributes:
    ------------

    player_dict: dict
        scrapped information from website goes into the dictionary of each player from the table
    image_dict: dict
        scrapped information from the links of the website into the dictionary of each player 
    """
    def __init__(self):
        #data structure
        self.changes = False
        self.player_dict = {'UUID': [],
                            'Rank': [],
                            'Player': [],
                            'Club': [],
                            'Nationality': [],
                            'Stat': [],
                            'Date Of Birth': [],
                            'Height': [],
                            'link': []
                            }

        self.image_dict = {'UUID': [],
                            'Image Name': [],
                            'Player Images': []
                            }
        
        #aws data upload
        self.client1 = boto3.client('s3')
        self.client2 = boto3.resource('s3')
        #storage location
        self.data_store = './raw_data'
        #Headless mode selenium webdriver
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    def visit_web(self, url):
        """
        This method visits the required website

        parameters:
        url: str
        The link which will be used to visit the website for scraping

        Attribute
        ---------
        driver:
        a webdriver object
        """
        #selenium webdriver for scraping
        self.url = url
        self.driver.get(self.url)
        #WebDriverWait(self.driver, 5).until(EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="mainContent"]/div[2]/div/div[2]/div[1]/div[2]')))
        self.driver.maximize_window()
        time.sleep(2)

    def connecting_to_RDS(self, creds: str='config/credentials.yaml'):
        """
        This method connects to the RDS using the database type and the user input

        Parameters:
        ----------
        None

        """
        with open(creds,'r') as f:
            creds = yaml.safe_load(f)
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        HOST = creds['HOST'] 
        DBUSER = creds['DBUSER'] 
        DBPASSWORD = creds['DBPASSWORD'] 
        PORT = 5432
        DATABASE = creds['DATABASE'] 
        self.engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{DBUSER}:{DBPASSWORD}@{HOST}:{PORT}/{DATABASE}")
        

        self.engine.connect()
        self.rds_player_table = pd.read_sql_table(
            'tbl_player_data', con=self.engine,
            columns=["index","UUID", "Rank", "Player", "Club",
                     "Nationality", "Stat", "Date Of Birth",
                     "Height", "link"])
        self.rds_player_table = (self.rds_player_table.sort_values('index')
                                .reset_index(drop=True))
        print("Player data from RDS")
        print(self.rds_player_table)
        self.rds_image_table = pd.read_sql_table(
            'tbl_image_data', con=self.engine,
            columns=["index","UUID", "Image Name", "Player Images"])
        self.rds_image_table = (self.rds_image_table.sort_values('index')
                                .reset_index(drop=True))
        print("Image data from RDS")
        print(self.rds_image_table)
    
    def accept_cookies(self, xpath: str='//button[@class="_2hTJ5th4dIYlveipSEMYHH BfdVlAo_cgSVjDUegen0F js-accept-all-close"]'):
        """
        This method looks for cookies on the website and clicks on the accept button
        
        Parameters
        ----------
        xpath: str
            the xpath of the accept cookies frame/button
        """
        try:
            #self.driver.switch_to.frame('')
            time.sleep(2)
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
            time.sleep(1)
            self.driver.find_element(By.XPATH, xpath).click()
            print("Cookies accepted")
        except TimeoutException:
            print("no cookies found")

    def scroll_page(self, x=0, y=300):
        """
        This method helps scroll the page by giving x and y values

        Parameters:
        ----------
        X: int
        Y: int
        """
        time.sleep(2)
        self.driver.execute_script(f'window.scrollBy({x},{y})')
    
    def storing_player_data(self, folder):
        """
        This method creates or checks a folder if it doesn't exist, where player information is stored in json format and as well as image of the players

        Parameters
        ----------
        folder: str
        """
        if not os.path.exists(folder):
            os.mkdir(folder)
    
    def player_data_list(self):
        """
        This method gets rank, player name, club, nationality, stats of a player from the table insdie the first page
        Parameters:
        ----------
        Returns:
        -------
        None

        """
        #getting player info from table insdie main page and storing in a dictionary
        time.sleep(1)
        try:
            rank_list = self.driver.find_elements(By.XPATH, '//table/tbody/tr/td/strong')
            self.player_dict['Rank'] = (self.player_dict['Rank']+[rank.text for rank in rank_list])
        except NoSuchElementException:
            self.player_dict['Rank']= (self.player_dict['Rank']+['N/A'])
        try:
            name_list = self.driver.find_elements(By.CLASS_NAME, "playerName")
            self.player_dict['Player']= (self.player_dict['Player']+[name.text for name in name_list])
        except NoSuchElementException:
            self.player_dict['Player']= (self.player_dict['Player']+['N/A'])
        try:
            club_list = self.driver.find_elements(By.CLASS_NAME, "statNameSecondary")
            self.player_dict['Club'] = (self.player_dict['Club']+[club.text for club in club_list])
        except NoSuchElementException:
            self.player_dict['Club'] = (self.player_dict['Club']+['N/A'])
        try:
            nationality_list = self.driver.find_elements(By.CLASS_NAME, 'playerCountry')
            self.player_dict['Nationality'] = (self.player_dict['Nationality']+[nationality.text for nationality in nationality_list])
        except NoSuchElementException:
            self.player_dict['Nationality'] = (self.player_dict['Nationality']+['N/A'])
        try:
            stat_list = self.driver.find_elements(By.XPATH, '//td[@class="mainStat text-centre"]')
            self.player_dict['Stat']= (self.player_dict['Stat']+[stat.text for stat in stat_list])
        except NoSuchElementException:
            self.player_dict['Stat'] = (self.player_dict['Stat']+['N/A'])
        
        print("Collected players information from the table")

    def player_links_uuid(self):
        """
        This method gets link from the table and gets the uuid from the link which creates a unique ID
        Parameters:
        ----------
        None
        """
        #getting only the player links from the table
        athlete_container = self.driver.find_element(By.XPATH, '//tbody[@class="statsTableContainer"]/tr')
        athlete_table = athlete_container.find_elements(By.XPATH, '//td[2]')
        self.player_links = []
        for player in athlete_table:
            time.sleep(1)
            a_tag = player.find_element(By.TAG_NAME, 'a')
            profile_links = a_tag.get_attribute('href')

            if profile_links in self.player_links:
                pass
            else:
                self.player_links.append(profile_links)
                self.player_dict['link'].append(profile_links)
                self.player_dict['UUID'].append(str(uuid.uuid4()))

        print("collected links for each players profile and UUID")
        
            
                
    def player_extra_data_and_images_data_from_links(self):
        """
        This method visits the link of each player from the table and gets extra info of each player and as well as their images
        and uploads the images to AWS S3

        Parameters:
        ----------
        None
        """
        #iterating through each player page and getting images and unique id and appending it to a dict called image_dict
        #and as well as getting extra player info and adding to player_dict dictionary

        for link in self.player_links[0:20]:
            self.driver.get(link)
            time.sleep(1)
            image_container = self.driver.find_element(By.XPATH, '//*[@id="mainContent"]/section/div[2]/div[1]')
            name = image_container.find_element(By.CLASS_NAME, 'img')
            self.name = name.get_attribute('alt')
            image = image_container.find_element(By.CLASS_NAME, 'img')
            self.source = image.get_attribute('src')
            self.storing_player_data(f'raw_data/{self.name}')

            #player extra data from pages
            try:
                dob_list = self.driver.find_elements(By.XPATH, "//section/div/ul[2]/li/div[2]")
                self.player_dict['Date Of Birth'] = (self.player_dict['Date Of Birth']+[dob.text for dob in dob_list])
            except NoSuchElementException:
                self.player_dict['Date Of Birth'].append('N/A')
            try:
                height_list = self.driver.find_elements(By.XPATH, "//div[3]/div/div/div[1]/section/div/ul[3]/li[1]/div[@class='info']")
                self.player_dict['Height'] = (self.player_dict['Height']+[height.text for height in height_list])
            except NoSuchElementException:
                self.player_dict['Height'].append('N/A')
            print(f"collected extra data from the profile of {self.name}")
            

            #image data
            try:
                self.image_dict['Image Name'].append(self.name)
            except NoSuchElementException:
                self.image_dict['Image Name'].append('N/A')
            try:
                image_list = []
                image_list.append(self.source)
            except NoSuchElementException:
                image_list = []
            for i in range(len(image_list)):
                time.sleep(1)
                new_id = str(uuid.uuid4())
                self.image_dict['UUID'].append(new_id)
                self.image_dict['Player Images'].append(image_list[i])
            print(f"collected image and uuid from the profile of {self.name}")
                

            #retrieving images from source    
            urllib.request.urlretrieve(self.source, f'raw_data/{self.name}/{self.name}.jpg')
            #upload images to aws s3
            #self.client1.upload_file((f'raw_data/{self.name}/{self.name}.jpg'), 'aicore-april', (f'raw_data/{self.name}/{self.name}.jpg'))
            print("Uploading images to AWS S3")

    def sort_scraping_image_data(self):
        """
        This method sort out the data collected stored in the image dictionary and transforms to panda dataframe

        Parameters:
        -----------
        None
        """
        self.image_dict = pd.DataFrame.from_dict(self.image_dict, orient='index')
        self.image_dict = self.image_dict.transpose()
    
    def indexing_image_data(self):
        """
        This method helps indexing the image dict so that it can be stored in the raw_data folder according to each player name
        and also uploads the image data to AWS S3
        Parameter:
        ---------
        None
        """
        for index in range(len(self.image_dict['Image Name'])):
            self.image_folder = self.image_dict['Image Name'][index].strip()
            self.storing_player_data(f'raw_data/{self.image_folder}')
            image_data = [{
                            "UUID": self.image_dict["UUID"][index],
                            "Image Name": self.image_dict["Image Name"][index],
                            "Player Images": self.image_dict["Player Images"][index]
                            
            }]
            if json.dump == False:
                with open(f'raw_data/{self.image_folder}/data.json','w') as f:
                    json.dump(image_data, f)
            else:
                json.dump == True
                print("Image data json files already exists")
            #uploading image data to s3 bucket
            #with open(f'raw_data/{self.image_folder}/data.json', 'rb') as data:
                #self.client1.put_object(Body=data, Bucket='aicore-april', Key= f'raw_data/{self.image_folder}/data.json')
            print("Uploading Image data to AWS S3")

    def sort_scraping_player_data(self):
        """
        This method sort out the data collected stored in the image dictionary and transforms to panda dataframe

        Parameters:
        -----------
        None
        """
        self.player_dict = pd.DataFrame.from_dict(self.player_dict, orient='index')
        self.player_dict = self.player_dict.transpose()
    
    def indexing_player_data(self):
        """
        This method helps indexing the player dict so that it can be stored in the raw_data folder according to each player name
        and uploads the player data to AWS S3
        Parameter:
        ---------
        None
        """
        for index in range(len(self.player_dict['Player'])):
            self.folder_name = self.player_dict['Player'][index].strip()
            self.storing_player_data(f'raw_data/{self.folder_name}/{self.folder_name}')
            #self.pull_image(folder_name)
            self.info_data = [{
                "UUID": self.player_dict["UUID"][index],
                "Rank": self.player_dict["Rank"][index],
                "Player": self.player_dict["Player"][index],
                "Club": self.player_dict["Club"][index],
                "Nationality": self.player_dict["Nationality"][index], 
                "Stat": self.player_dict["Stat"][index],
                "Date Of Birth": self.player_dict["Date Of Birth"][index],
                "Height": self.player_dict["Height"][index],
                "link": self.player_dict["link"][index]
            }]
            if json.dump == False:
                with open(f'raw_data/{self.folder_name}/{self.folder_name}/data.json','w') as f:
                    json.dump(self.info_data, f)
            else:
                json.dump == True
                print("player data (json) files already exists")
                
            #uploading player data to s3 bucket
            #with open(f'raw_data/{self.folder_name}/{self.folder_name}/data.json', 'rb') as data:
                #self.client1.put_object(Body=data, Bucket='aicore-april', Key= f'raw_data/{self.folder_name}/{self.folder_name}/data.json') 
            print("Uploading Player data to AWS S3")

    def check_player_data_difference(self):
        if len(self.player_dict) != len(self.rds_player_table):
            return True
        else:
            self.player_dict['Same Result'] = (np.where(self.player_dict['Rank'],1,0))
            if (sum(self.player_dict['Same Result']) == len(self.player_dict['Same Result'])):
                self.player_dict['Same Result'] = (np.where(self.player_dict['Player'] == self.rds_player_table['Player'],1,0))
                if (sum(self.player_dict['Same Result']) == len(self.player_dict['Same Result'])):
                    self.player_dict['Same Result'] = (np.where(self.player_dict['Club'] == self.rds_player_table['Club'],1,0))
                    if (sum(self.player_dict['Same Result']) == len(self.player_dict['Same Result'])):
                        self.player_dict['Same Result'] = (np.where(self.player_dict['Nationality'] == self.rds_player_table['Nationality'],1,0))
                        if (sum(self.player_dict['Same Result']) == len(self.player_dict['Same Result'])):
                            self.player_dict['Same Result'] = (np.where(self.player_dict['Stat'] == self.rds_player_table['Stat'],1,0))
                            if (sum(self.player_dict['Same Result']) == len(self.player_dict['Same Result'])):
                                self.player_dict['Same Result'] = (np.where(self.player_dict['Date Of Birth'] == self.rds_player_table['Date Of Birth'],1,0))
                                if (sum(self.player_dict['Same Result']) == len(self.player_dict['Same Result'])):
                                    self.player_dict['Same Result'] = (np.where(self.player_dict['Height'] == self.rds_player_table['Height'],1,0))
                                    print("Same results, nothing to rescrape")
                                    return False
        print("Different Result, Need to Rescrape")
        return True
     
    def upload_RDS_table(self):
        time.sleep(1)
        self.df_player_table = self.player_dict
        self.df_player_table.to_sql('tbl_player_data', con = self.engine, if_exists='replace')
        print("player data added to RDS")
        self.df_image_table = self.image_dict
        self.df_image_table.to_sql('tbl_image_data', con = self.engine, if_exists='replace')
        print("Image data added to RDS")


if __name__ == '__main__':
    #bot = Scraper("https://www.premierleague.com/stats/top/players/goals?se=418")
    upload_to_cloud_sevices = False
    Test = False
    if Test is False:
        premier_league = Scraper()
        premier_league.connecting_to_RDS()
        url = "https://www.premierleague.com/stats/top/players/goals?se=418"
        premier_league.visit_web(url)
        premier_league.accept_cookies()
        premier_league.scroll_page()
        premier_league.storing_player_data('raw_data')
        premier_league.player_data_list()
        premier_league.player_links_uuid()
        premier_league.player_extra_data_and_images_data_from_links()
        premier_league.sort_scraping_image_data()
        print("Scraped Image Data")
        premier_league.indexing_image_data()
        premier_league.sort_scraping_player_data()
        print("Scraped Player Data")
        premier_league.indexing_player_data()
        if premier_league.check_player_data_difference():
            print("Different Output, Rescrape in progress")
            premier_league.indexing_player_data()
            premier_league.upload_RDS_table()
        else:
            print("Test Complete, Scraped successfully")
    else:
        premier_league = Scraper("https://www.premierleague.com/stats/top/players/goals?se=418")
        premier_league.upload_RDS_table()

# %%
