#!pip install selenium
#!apt-get update 
#!apt install chromium-chromedriver

#!pip install scrapy

import requests
import scrapy
from scrapy import Selector

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from datetime import datetime
import pandas as pd
import numpy as np
import requests
import openpyxl
from bs4 import BeautifulSoup
import pandas as pd
import urllib.request
import re
import math 


class get_TA_help():
  '''Makes the link and summary table for Tripadvisor. 
  This helps in choosing the reviews to choose on the basis of ratings and number of reviews'''

  def __init__(self, OUTPUT_FILE = 'TA_summary.csv'):
    self.column_list = ['name','url','overall_rating','reviews']
    self.df_airlines = pd.DataFrame(columns= self.column_list)
    self.url_list = []
    self.create_driver_for_colab()
    self.get_TA_links()
    self.get_TA_summary()
    self.summary.to_csv(OUTPUT_FILE)

  def create_driver_for_colab(self):
    '''create connection for collab notebook'''
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    wd = webdriver.Chrome('chromedriver',chrome_options=chrome_options)
    self.driver =webdriver.Chrome('chromedriver',chrome_options=chrome_options)

  def get_TA_links(self):
    ''''''
    self.driver.get("https://www.tripadvisor.com/Airlines")
    for i in range(61):
      airlines = self.driver.find_elements_by_xpath('//div[contains(@class,"prw_airlines_airline_lander_card")]/div/div[1]/div[1]/a[1]')
      for al in airlines:
        self.url_list.append((al.text,al.get_attribute('href')))
        self.driver.find_element_by_xpath('//span[contains(@class,"next")]').click()
        sleep(3)
        
  def get_TA_summary(self):
    url_list =  self.url_list
    for i in range(len(self.url_list)):
      if self.url_list[i][0] not in ['Atlas Atlantique [no longer operating]','Colorful GuiZhou Airlines','Genghis Khan',
                                'JetClass','Jiangxi Air','Nesma Airlines Saudi Arabia','NewGen Airways','Pan Pacific',
                                'Royal Air Philippines','Wasaya Airways']:
        
        self.driver.get(self.url_list[i][1])
        review = self.driver.find_element_by_xpath('//span[contains(@class,"reviewCount")]').text.split()[0]
        rating = self.driver.find_element_by_xpath('//*[@id="component_1"]/div/div[6]/div/div/div/div[1]/div/div[2]/div/div/div/div[2]/div[1]/div[1]/div[1]/span[1]').text
        self.df_airlines = pd.concat([self.df_airlines, pd.DataFrame({'name': [url_list[i][0]], 'url':[url_list[i][1]], 
                                        'overall_rating':[rating],'reviews':[review]},
                                        columns = column_list)],ignore_index = True)

  


class get_SG_data():
  ''''''
  def __init__(self,OUTPUT_FILE = 'SG_data.csv'):
    self.WEBSITE_URL = 'https://www.seatguru.com'
    self.col_list = ['Airlines','main_link','Plane_type','pt_link']
    self.sg_links_df = pd.DataFrame(columns = self.col_list)
    self.name_list, self.url_list_SG = self.get_airlines_url()
    self.get_link_df()
    self.col_list2 = ['Airlines','main_link','Plane_type','pt_link','date_seat','comment']
    self.sg_df = pd.DataFrame(columns = self.col_list2)
    self.get_final_df()
    self.sg_df.to_csv(OUTPUT_FILE)


  def get_airlines_url(self):
    html = requests.get('https://www.seatguru.com/browseairlines/browseairlines.php').content
    sel_SG = Selector(text = html)
    name_list  = sel_SG.css('div.browseAirlines li > a::text').extract()
    url_list_SG = sel_SG.css('div.browseAirlines li > a::attr(href)').extract()
    return name_list,url_list_SG

  def get_link_df(self):
    for i in range(len(self.name_list)):
      geturl = self.WEBSITE_URL + self.url_list_SG[i]
      html = requests.get(geturl).content
      sel = Selector(text = html)
      planes = sel.css('div.aircraft_seats > a::text').extract()
      planes_link = sel.css('div.aircraft_seats > a::attr(href)').extract()
      self.sg_links_df = pd.concat([self.sg_links_df, pd.DataFrame({'Airlines': [self.name_list[i]]*len(planes), 
                                                                    'main_link':[self.url_list_SG[i]]*len(planes), 
                                                                    'Plane_type':planes,
                                                                    'pt_link':planes_link},
                                                                   columns = self.col_list)],ignore_index = True)
  def get_final_df(self):
    for index,row in self.sg_links_df.iterrows():
      reviews_url = self.WEBSITE_URL + row['pt_link']
      print(index,row['pt_link'])
      html = requests.get(reviews_url).content
      sel = Selector(text = html)
      seat_date = sel.css('div.submitted > span:nth-of-type(3)::text').extract()
      comment = sel.css('div.comment::text').extract()
      if not (len(seat_date)==0 and len(comment)==0):
        num_rows = max(len(seat_date)==0,len(comment)==0)
        self.sg_df = pd.concat([self.sg_df, pd.DataFrame({'Airlines': row['Airlines'] , 
                                                          'main_link': row['main_link'] , 
                                                          'Plane_type': row['Plane_type'],
                                                          'pt_link': row['pt_link'] ,
                                                          'date_seat': seat_date,
                                                          'comment':comment},
                                                          columns = self.col_list2)],ignore_index = True)

      
class get_AQ_data():

  def __init__(self,airline_reviews= True,seat_reviews = True,OUTPUT_FILE_SEAT = 'AQS_data.csv',OUTPUT_FILE_AIRLINES = 'AQA_data.csv'):
    
    self.airline_reviews = airline_reviews
    self.seat_reviews = seat_reviews
    self.OUTPUT_FILE_SEAT = OUTPUT_FILE_SEAT
    self.OUTPUT_FILE_AIRLINES = OUTPUT_FILE_AIRLINES
    
    if self.seat_reviews:
      self.baseUrl = 'https://www.airlinequality.com/seat-reviews/'
      self.A_Z_LIST = 'https://www.airlinequality.com/review-pages/a-z-seat-reviews/'
      self.airlines = []
      self.get_airline_list()
      columns_list = ['airline', 'title', 'date', 'content', 'rate']
      self.AQ_seat_reviews = pd.DataFrame(columns=columns_list)
      self.get_seat_reviews()
    
    if self.airline_reviews:
      self.baseUrl = 'https://www.airlinequality.com/airline-reviews/'
      self.A_Z_LIST = 'https://www.airlinequality.com/review-pages/a-z-airline-reviews/'
      self.airlines = []
      self.get_airline_list()
      columns_list = ['airline', 'title', 'date', 'content', 'rate', 'TypeOfTraveller','SeatType']
      self.AQ_airlines_reviews = pd.DataFrame(columns=columns_list)
      self.get_airline_reviews()


  def get_airline_list(self):
    res = requests.get(A_Z_LIST)
    soup2 = BeautifulSoup(res.text, 'html.parser')

    for list in soup2.select("div.a_z_col_group > ul.items > li > a"):
      airline = list.get_text().lower().strip().replace(" ","-")
      self.airlines.append(airline)


  
  def lastPage(airline_name):
    plusUrl = airline_name
    url = self.baseUrl + urllib.parse.quote_plus(airline_name)
    req = requests.get(url)
    data = BeautifulSoup(req.text, 'html.parser')
    reviewCount = int(re.findall("\d+", data.find(attrs={'itemprop':'reviewCount'}).text)[0])
    lastPage = math.ceil(reviewCount/10)
    return lastPage
    
  def airline_reviews(airline):

    basic_final = list()
    title_final = list()
    date_final = list()
    content_final = list()
    airline_final = list()
    rate_final = list()
    PageNum = 1
    lastpage = self.lastPage(airline)

    while PageNum < lastpage + 1:

      res = requests.get(
          f"{self.baseUrl}{airline}/page/{PageNum}/")
      soup = BeautifulSoup(res.text, 'html.parser')

      # rate
      all = soup.find_all("div",{"class":"rating-10"})
      for x in all:
        try:
          rate_final.append(x.find("span", {"itemprop":"ratingValue"}).get_text())
        except:
          rate_final.append('NA')
      rate_final = [i for i in rate_final if len(i)<=2 or i=='NA']
    

      # airline, title, content, date
      review = soup.select("div.body")
      for data in review:
        airline_final.append(airline)
        title = data.select_one('h2').get_text()
        title_final.append(title)
        date = data.select_one('time').get_text()
        date_final.append(date)
        content = data.select_one('div.text_content').get_text()
        content_final.append(content)
        table = data.find_all("tr")
        SeatType = table[0].find_all("td")[1].get_text()
        AircraftType = table[1].find_all("td")[1].get_text()
        SeatLayout = table[2].find_all("td")[1].get_text()
      
        #type = soup.select_one('td:contains("Type Of Traveller") + td').text
      
      PageNum += 1

    table = pd.DataFrame({'airline':airline_final, 'title':title_final, 'date':date_final, 'content':content_final, 'rate':rate_final,
                          'SeatType':SeatType,'AircraftType':AircraftType, 'SeatLayout':SeatLayout })
    return table

  def get_seat_reviews(self):
    not_working = ['atlasglobal','azul-airlines','air-canada-rouge','boliviana-de-aviacion','hk-express','indigo',
                    'middle-east-airlines','pakistan-intl-airlines','sas-scandinavian','sata-international',
                    'small-planet-airlines','swiss-intl-air-lines','ukraine-international','vietjet-air',
                    'virgin-atlantic','westjet-airlines']
    i = 0
    for al in self.airlines[i:]:
      i+=1
      if al not in not_working:
        self.AQ_seat_reviews = pd.concat([self.AQ_seat_reviews,self.airline_reviews(al)])
        print(al,'\t',self.AQ_seat_reviews.shape)
        self.AQ_airlines_reviews.to_csv(self.OUTPUT_FILE_SEAT)

    def get_airline_revies(self):
    list_al = ['qatar-airways', 'airasia','ana-all-nippon-airways','british-airways','emirates',
            'eva-air','hainan-airlines','qantas-airways','lufthansa','thai-airways','japan-airlines',
            'garuda-indonesia','china-southern-airlines','austrian-airlines',
            'air-new-zealand','air-france','bangkok-airways','klm-royal-dutch-airlines','cathay-pacific-airways']
            
    i = 0
    for al in list_al[i:]:
        i+=1
        self.AQ_airlines_reviews = pd.concat([self.AQ_airlines_reviews,self.airline_reviews(al)])
        print(al,'\t',self.AQ_airlines_reviews.shape)
        self.AQ_airlines_reviews.to_csv(self.OUTPUT_FILE_AIRLINES)

def main():
    get_TA_help()
    get_SG_data()
    get_AQ_data()

if __name__ == "__main__":
    main() 
