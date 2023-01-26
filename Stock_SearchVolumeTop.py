import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_url_page(url):
  result_get = requests.get(url)
  result_get.raise_for_status()
  return BeautifulSoup(result_get.text, "lxml")

def analysis_item(url_item):
  # 종목 페이지 읽기
  soup = get_url_page(url_item)

  # 업종을 추출
  data = soup.find("h4", attrs={"class":"h_sub sub_tit7"})
  if data != None:
    data = data.find("a").text

  return data

def make_list(type):
  # 코스피/코스닥이 아니면 미실행
  if type != 0 and type != 1:
    return

  # 네이버 거래상위 종목 URL
  # 코스피 https://finance.naver.com/sise/sise_quant.naver?sosok=0
  # 코스닥 https://finance.naver.com/sise/sise_quant.naver?sosok=1
  url_volume = "https://finance.naver.com/sise/sise_quant.naver?sosok="
  
  # 코스피/코스닥 거래상위 페이지 읽기
  soup = get_url_page(url_volume + str(type))

  # 제목 행
  title = "N,종목명,현재가,전일비,등락률,거래량,거래대금,매수호가,매도호가,시가총액,PER,ROE,업종,종목페이지".split(",")
  writer.writerow(title)

  # 거래상위 테이블
  data_rows = soup.find("table", attrs={"class":"type_2"}).find_all("tr")
  for row in data_rows:
    columns = row.find_all("td")

    # 의미없는 데이터는 skip
    if len(columns) <= 1: 
      continue

    # 거래량 일 10,000,000주 이상만 수집
    if int(columns[5].get_text().strip().replace(',', '')) < 10000000:
      break;

    # 거래상위 종목 기록
    item = [column.get_text().strip() for column in columns]
    url_item_detail = "https://finance.naver.com" + columns[1].find("a")['href']
    item.append(analysis_item(url_item_detail))
    item.append(url_item_detail)
    writer.writerow(item)
  
  if type == 0:
    writer.writerow("")

# 거래상위 종목을 저장할 파일 지정 및 OPEN
filename = "거래상위_ " + datetime.today().strftime("%Y%m%d") + ".csv"
f = open(filename, "w", encoding="utf-8-sig", newline="")
writer = csv.writer(f)

for type in range(0, 2):
  make_list(type)

f.close()
