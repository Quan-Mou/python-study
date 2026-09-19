import requests
from lxml import html

"""
    xpath解析网页
"""

response = requests.get("https://www.tiobe.com/tiobe-index/")
html_content = response.text
document = html.fromstring(html_content)

# table_head = document.xpath("//table/thead/tr/th/text()")
# //table[@class='table table-striped table-top20']/tbody/tr[1]/td/text() 获取第第一个tr的元素
table_head = document.xpath("//table[@class='table table-striped table-top20']/thead/tr/th/text()")
table_body = document.xpath("//table[@class='table table-striped table-top20']/tbody/tr")
print(f"列表长度{len(table_body)}")
print(table_head)

for item in table_body:
    print(item.xpath("./td/text()"))





