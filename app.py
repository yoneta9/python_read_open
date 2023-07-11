import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import pybase64
import requests
from bs4 import BeautifulSoup
import math
from time import sleep

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
    

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# セッションステートの初期化
if "search_word" not in st.session_state:
    st.session_state.search_word = ""

if "submit_btn" not in st.session_state:
    st.session_state.submit_btn = False

if "search_btn" not in st.session_state:
    st.session_state.search_btn = False

if "report_table" not in st.session_state:
    st.session_state.report_table = False

if "output_btn" not in st.session_state:
    st.session_state.output_btn = False

# イントロダクション
st.title("論文抽出＆翻訳サービス")
st.caption("こちらは医療論文サイトpubmedから検索条件にマッチした論文を抽出し翻訳できるサービスです")

with st.form(key="input_form"):
    st.session_state.search_word = st.text_input("検索ワードを入力してください", value=st.session_state.search_word)
    if st.form_submit_button("検索開始"):
      st.session_state.submit_btn = True
    st.caption("point1: 検索ワードは「(検索ワード1) AND (検索ワード2)」のような形で記載してください。")
    st.caption("point2: pubmed内の'AdvancedSearchBuilder'で作成すると簡単です。")
