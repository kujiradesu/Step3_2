#ライブラリのインポート
from bs4 import BeautifulSoup
import re #不要文字削除
import requests
from time import sleep
import time
from tqdm import tqdm   #for文の進捗確認
import pandas as pd

url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&pc=30&smk=&po1=25&po2=99&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sc=13101&sc=13102&sc=13103&sc=13104&sc=13105&sc=13113&sc=13106&sc=13107&sc=13108&sc=13118&sc=13121&sc=13122&sc=13123&sc=13109&sc=13110&sc=13111&sc=13112&sc=13114&sc=13115&sc=13120&sc=13116&sc=13117&sc=13119&ta=13&cb=0.0&ct=20.0&md=05&md=06&md=07&md=08&md=09&et=10&mb=0&mt=9999999&cn=15&tc=0400301&fw2="
res = requests.get(url)
res.encoding = 'utf-8'
soup = BeautifulSoup(res.text, 'html.parser')
maxpage = int(soup.select("ol.pagination-parts a")[-1].text)

# 正常にHTML情報が取得できれば以下のコードを実行
if res.status_code == 200:

    names = []
    addresses = []
    access = []
    ages = []
    maxfloors = []

    floors = []
    rents = []
    layouts = []
    sizes = []


    for x in range(maxpage):
        res = requests.get(url+"&page="+str(x))
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        suumo_cassetteitem_from_html = soup.select('div.cassetteitem')
        time.sleep(1)

        for sc in suumo_cassetteitem_from_html:
            suumo_name = sc.select('div.cassetteitem_content-title')[0].text
            suumo_address = sc.select("li.cassetteitem_detail-col1")[0].text
            suumo_access = sc.select('li.cassetteitem_detail-col2')[0].text.replace('\n',',').strip(',')
            suumo_age, suumo_maxfloor = sc.select("li.cassetteitem_detail-col3")[0].text.split()

            tbody_items = sc.select('tbody')

            for ti in tbody_items:
                suumo_floor = ti.select('tr.js-cassette_link')[0].text.split()[0]
                suumo_rent = ti.select('span.cassetteitem_other-emphasis, span.ui-text--bold')[0].text
                suumo_layout = ti.select('span.cassetteitem_madori')[0].text
                suumo_size = ti.select('span.cassetteitem_menseki')[0].text

                names.append(suumo_name)
                addresses.append(suumo_address)
                access.append(suumo_access)
                ages.append(suumo_age)
                maxfloors.append(suumo_maxfloor)
                floors.append(suumo_floor)
                rents.append(suumo_rent)
                layouts.append(suumo_layout)
                sizes.append(suumo_size)

        data = {
        'Name': names,
        'Address': addresses,
        'Access': access,
        'Age': ages,
        'Max_Floor': maxfloors,
        'Floor': floors,
        'Rent': rents,
        'Layout': layouts,
        'Size': sizes
    }

df = pd.DataFrame(data)

#google spread sheets 出力
#ライブラリのインポート
import gspread
from oauth2client.service_account import ServiceAccountCredentials

#環境変数関連
from dotenv import load_dotenv
load_dotenv()
import os

#スコープとjsonファイルを使って認証情報を取得
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
#SERVICE_ACCOUNT_FILE = '/Users/maedaryo/step3/tech0-step3-407115-94fd3b930a55.json'
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)

#認証情報をauthorize関数に渡してスプレッドシートの操作権を取得
gs = gspread.authorize(credentials)

#シート情報を取得して変数に代入
SPREADSHEET_KEY = os.getenv("SPREADSHEET_KEY")
workbook = gs.open_by_key(SPREADSHEET_KEY)
worksheet = workbook.worksheet("db")

#特定の列（'Address', 'Floor', 'Rent', 'Layout', 'Size'）に基づいて重複する行を削除
df.drop_duplicates(subset=['Address', 'Floor', 'Rent', 'Layout', 'Size'], inplace=True)

values = [df.columns.values.tolist()] + df.values.tolist()

worksheet.update("A1", values)

#SQLite
import sqlite3
conn = sqlite3.connect('fudosan.db')
df.to_sql('suumo', conn, if_exists='replace', index=False)
conn.close()
