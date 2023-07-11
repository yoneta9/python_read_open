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
    st.caption("point3: 検索結果が0の場合、エラーが発生した場合、検索ワードを変更したい場合は、更新ボタンか「F5」ボタンを押してください。")


if st.session_state.submit_btn:
    st.text("検索結果を下記にお示しします。")
    from scrape import scrape_search_num
    with st.form(key="middle_form"):
      st.markdown("<strong>:red[{0}]</strong>".format(scrape_search_num(st.session_state.search_word))+'件該当しました。このまま進めてよろしいでしょうか？', unsafe_allow_html=True)
      st.caption("検索に時間がかかるため検索結果が50件程度で実行されることをおすすめします。")
      if st.form_submit_button("実行する"):
        st.session_state.search_btn = True

if st.session_state.search_btn:
  st.text("それでは引き続きデータの集約と翻訳を進めて参ります。")
  from scrape import scrape_data
  df = scrape_data(st.session_state.search_word)
  df['Published_year'] = df['Published'].str[0:4]
  df = df.sort_values('Published_year')
  fig, ax = plt.subplots(figsize=(8,4))
  ax.set_title('publish monthly graph')
  sns.countplot(data=df, x="Published_year",ax=ax)
  st.pyplot(fig)
  df1 = df[["タイトル","要約","Published_year","URL"]]
  st.text("タイトル・要約等を下記にまとめました。隠れている箇所は左ダブルクリックいただくと詳細を確認できます。")
  st.dataframe(df1)
  if len(df1)>0:
    report_table = np.nan
    st.session_state.report_table  = True

if st.session_state.report_table:
  with st.form(key="output_form"):
    st.text("検索結果はいかがでしたでしょうか？　保存されたい方は、下記に保存ファイル名をご入力ください")
    search_title = st.text_input("作成するファイル名を入力してください")
    if st.form_submit_button("CSVデータ作成"):
      st.session_state.output_btn = True
    st.caption("「Pubmed_{指定されたファイル名}_{本日の日付}.csv」という形で出力されます。")
    st.caption("ファイルの作成には少し時間がかかります")

if st.session_state.output_btn:
  if search_title:
      csv_date = datetime.datetime.today().strftime("%Y%m%d")
      csv_file_name = "Pubmed_" + search_title +"_" +csv_date + ".csv"

      csv = df.to_csv(index=False)
      b64 = pybase64.b64encode(csv.encode('utf-8-sig')).decode()
      href = f'<a href="data:application/octet-stream;base64,{b64}" download={csv_file_name}>Download Link</a>'
      st.markdown(f"CSVファイルのダウンロード(utf-8 BOM):  {href}", unsafe_allow_html=True)
  else:
      st.text("保存ファイル名を入力してください")
