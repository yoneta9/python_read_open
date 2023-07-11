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
    
#翻訳用のライブラリを読み込んでいく
from easynmt import EasyNMT
model = EasyNMT('opus-mt')

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
      
if st.session_state.submit_btn:
    st.text("検索結果を下記にお示しします。")
   # from scrape import scrape_search_num
    with st.form(key="middle_form"):
      st.markdown("<strong>:red[{0}]</strong>".format(scrape_search_num(st.session_state.search_word))+'件該当しました。このまま進めてよろしいでしょうか？', unsafe_allow_html=True)
      st.caption("検索に時間がかかるため検索結果が50件程度で実行されることをおすすめします。")
      if st.form_submit_button("実行する"):
        st.session_state.search_btn = True
