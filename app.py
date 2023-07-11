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
#model = EasyNMT('mbart50_m2m')
