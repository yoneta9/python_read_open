#必要なライブラリを読み込んでいく
import requests
from beautifulsoup4 import BeautifulSoup
import pandas as pd
import datetime
import math
from time import sleep
import numpy as np

#翻訳用のライブラリを読み込んでいく
from easynmt import EasyNMT
model = EasyNMT('mbart50_m2m')


def scrape_search_num(search_word):
  if search_word:
    base_url = "https://pubmed.ncbi.nlm.nih.gov"
    search_url = base_url + "/?term=" + search_word

    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    value_span = soup.find('span', class_='value')
    return int(value_span.get_text())
  else:
    pass

def scrape_data(search_word):
  base_url = "https://pubmed.ncbi.nlm.nih.gov"
  search_url = base_url + "/?term=" + search_word
  articles = []


  response = requests.get(search_url)
  soup = BeautifulSoup(response.text, 'html.parser')

  value_span = soup.find('span', class_='value')
  value_span_num_int = int(value_span.get_text())
  value_span_nums = math.ceil(value_span_num_int/10)
  print('{0}件ヒットした'.format(value_span_num_int))
  for value_span_num in range(1,value_span_nums+1):
    search_url2 = search_url + '&page=' +str(value_span_num)
    # search_url2 = search_url + '&page=1'
    print('{0}ページ目をスクレイピング中'.format(value_span_num))
    response = requests.get(search_url2)
    soup = BeautifulSoup(response.text, 'html.parser')
    sleep(2)
    # soup3 =BeautifulSoup(driver.page_source,"html.parser")
    content = soup.find("div", class_="search-results-chunk results-chunk")
    for article in content.find_all('a', class_='docsum-title'):
        article_url = base_url + article.get('href')
        article_response = requests.get(article_url)
        article_soup = BeautifulSoup(article_response.text, 'html.parser')
        article_soup2 = article_soup.find("main", class_="article-details")
        sleep(2)
        try:
            title = article_soup2.find('h1', class_='heading-title').get_text(strip=True)
        except AttributeError:
            title = ""

        try:
            author = article_soup2.find('div', class_='authors-list').get_text(strip=True)
        except AttributeError:
            author = ""

        try:
            abstract = article_soup2.find('div', class_='abstract-content selected').get_text(strip=True)
        except AttributeError:
            abstract = ""

        try:
            publishid = article_soup2.find('span', class_="cit").get_text(strip=True)
        except AttributeError:
            publishid = ""

        try:
            pmid = article_soup2.find('strong', class_="current-id").get_text(strip=True)
        except AttributeError:
            pmid = ""

        articles.append([title, author, abstract,publishid,pmid,article_url])
  df = pd.DataFrame(articles, columns=['title', 'author', 'abstract','Published','PMID','URL'])

  #翻訳していく
  def translate_text(x):
    if x ==np.nan:
      return x
    else:
      x = model.translate(x, target_lang='ja')
      
      return x
  df['タイトル'] = df['title'].apply(translate_text)
  df['要約'] = df['abstract'].apply(translate_text)
  return df
