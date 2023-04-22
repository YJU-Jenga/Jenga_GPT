import pymysql
from bs4 import BeautifulSoup
import requests
import time
import config


def get_title_list(page_number):
    URL = f"http://18children.president.pa.go.kr/our_space/fairy_tales.php?srh%5Bcategory%5D=07&srh%5Bpage%5D={page_number}"
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    return [title.text.strip().replace(" ", "") for title in soup.select(".title > a")]


def get_content_list(page_number):
    URL = f"http://18children.president.pa.go.kr/our_space/fairy_tales.php?srh%5Bcategory%5D=07&srh%5Bpage%5D={page_number}"
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    return [content.text.strip() for content in soup.select(".txt > a")]


start = time.time()
maximum_page = 20
title_list = [title for page_number in range(1, maximum_page + 1) for title in get_title_list(page_number)]
content_list = [content for page_number in range(1, maximum_page + 1) for content in get_content_list(page_number)]
end = time.time()

print(f"{end - start:.5f} sec")
print(title_list)
print(content_list)

# Connect to database
db = pymysql.Connect(
    host='localhost',
    user='jenga',
    password=config.database_password,
    database='jenga',
    charset='utf8',
)
cursor = db.cursor()

sql = "TRUNCATE TABLE book"
cursor.execute(sql)

sql = "INSERT INTO book (title, detail) VALUES (%s, %s)"
for title, detail in zip(title_list, content_list):
    cursor.execute(sql, (title, detail))
db.commit()
db.close()
