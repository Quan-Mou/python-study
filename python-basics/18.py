
import requests
import time
from lxml import html
BASE_URL = "https://www.themoviedb.org/"
HIGH_SCORE = BASE_URL+  "/movie/top-rated"

TOP_AMOUNT = 100 # 前100条数据,每页20，需要5页

start_page = 1 # 起始页面

# html_info = requests.get(HIGH_SCORE,timeout=60)
# print(html_info)
# # docuemnt = html.fromstring(html_info.text)
# print(html_info.text)
# docuemnt = html.fromstring(html_info.text)


# link_list = []


"""
 1.先获取100页的详情列表
 2.在遍历这100页的详情页获取具体的数据
"""

# movie_list = docuemnt.xpath("//div[contains(@class,'media-list-results')]//h2[contains(@class,'font-semibold')]/parent::a")
# for item in movie_list:
#     link_list.append(item.get("href"))

def get_link(url):
    return requests.get(url).text



def fetch_movie_list():
    link_list = []
    start_page = 1
    page = 1
    while start_page <= TOP_AMOUNT:
        url = HIGH_SCORE + "?page=" + str(page)
        print(f"正在获取第{start_page}页的数据,url是{url}")
        text = get_link(url)
        # html_fromString()
        docuemnt = html.fromstring(text)
        moive_list = docuemnt.xpath("//div[contains(@class,'media-list-results')]//h2[contains(@class,'font-semibold')]/parent::a")
        for item in moive_list:
            link = item.get("href")
            print(BASE_URL + link)
            link_list.append(BASE_URL + link)
            
            start_page+=1
        time.sleep(0.5)
        page+=1  
        
    return link_list           
    
def main():
    # 
    link_list = fetch_movie_list()
    print(f"list len: {len(link_list)}")
    # pass


if "__main__" == __name__:
    main()

