"""
    获取https://www.themoviedb.org/movie/top-rated 这个网站榜单的top100的数据
    数据包括：电影名、年份、上映时间、类型、时长、评分、语言、导演、作者、主演、slogan、简介
    ，并且保存在csv文件中
"""

import csv  # 导入csv模块，用于把结果写入csv文件
import json  # 导入json模块，用于解析详情页中的 JSON-LD 结构化数据
import re  # 导入正则模块，用于从<script>标签中提取JSON字符串
import time  # 导入time模块，用于每次请求之间休眠，避免请求过快被封

import requests  # 导入requests库，用于发送HTTP请求获取网页
from lxml import html  # 导入lxml的html模块，用于xpath解析网页

BASE_URL = "https://www.themoviedb.org"  # TMDB网站根地址，用于拼接详情页的相对链接
LIST_URL = BASE_URL + "/movie/top-rated"  # 榜单列表页地址
CSV_FILE = "tmdb_top100.csv"  # 最终保存结果的csv文件名
TOP_N = 100  # 需要抓取的电影数量
PER_PAGE = 20  # 榜单每页显示20部电影

# 定义请求头：伪装浏览器User-Agent，并要求返回中文页面
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",  # 浏览器UA，防止被网站拒绝访问
    "Accept-Language": "zh-CN,zh;q=0.9",  # 希望网站返回中文内容（电影名、简介等为中文）
}

# "作者"对应的职位关键词（详情页中职位文本是英文），命中任意一个即认为是作者
WRITER_JOBS = ("screenplay", "writer", "story", "novel", "author", "book", "theatre play", "comic book", "characters")

session = requests.Session()  # 创建会话对象，复用TCP连接并统一携带请求头
session.headers.update(HEADERS)  # 把请求头设置到会话上，之后所有请求都生效


def fetch(url):
    """请求一个网址并返回网页文本，失败时自动重试3次"""
    for i in range(3):  # 最多尝试3次
        try:  # 尝试发送请求
            resp = session.get(url, timeout=15)  # 发送GET请求，超时时间15秒
            resp.raise_for_status()  # 如果HTTP状态码不是200则抛出异常
            return resp.text  # 请求成功，返回网页HTML文本
        except requests.RequestException as e:  # 捕获网络异常（超时、404、连接失败等）
            print(f"请求失败({i + 1}/3) {url}: {e}")  # 打印失败信息，方便排查
            time.sleep(2)  # 失败后等2秒再重试
    return ""  # 3次都失败则返回空字符串


def get_top100_links():
    """从榜单列表页获取top100电影的详情页链接"""
    links = []  # 存放(详情页链接, 榜单页标题)元组的列表
    page = 1  # 当前页码，从第1页开始
    while len(links) < TOP_N:  # 循环直到收集满100部电影
        url = f"{LIST_URL}?page={page}"  # 拼接分页地址，如 ?page=2
        print(f"正在获取榜单第{page}页: {url}")  # 打印进度提示
        text = fetch(url)  # 下载列表页HTML
        if not text:  # 如果下载失败
            break  # 退出循环
        doc = html.fromstring(text)  # 把HTML解析成可以xpath查询的文档对象
        # 每张卡片的结构是 <a href="/movie/xxx"><h2 class="font-semibold...">电影名</h2></a>
        cards = doc.xpath('//div[contains(@class,"media-list-results")]//h2[contains(@class,"font-semibold")]/parent::a')  # 取出所有电影卡片的<a>标签
        for a in cards:  # 遍历每个<a>标签
            href = a.get("href", "")  # 读取href属性，即详情页相对路径
            title = a.xpath("./h2/text()")  # 读取h2内的电影名文本
            title = title[0].strip() if title else ""  # 取第一个匹配并去掉首尾空白，没有则为空串
            if href.startswith("/movie/"):  # 只保留电影详情页链接，过滤广告等无效链接
                links.append((BASE_URL + href, title))  # 拼成完整网址后加入列表
        page += 1  # 页码加1，准备抓下一页
        time.sleep(0.5)  # 每页之间休息0.5秒，礼貌抓取
    return links[:TOP_N]  # 最多返回前100条


def parse_facts(doc):
    """解析详情页左侧'事实栏'，返回 {标签: 值} 字典（如 默认语言->英语）"""
    facts = {}  # 存放结果的字典
    for p in doc.xpath('//section[contains(@class,"facts left_column")]//p[bdi]'):  # 遍历事实栏中每个带<bdi>标签的段落
        label = p.xpath("./strong//bdi/text()")  # 取出<bdi>里的标签文字，如"默认语言"、"状态"
        label = label[0].strip() if label else ""  # 取第一个标签并去空白
        value = p.text_content().strip()  # 取整个段落的纯文本，如"默认语言 英语"
        if label and value.startswith(label):  # 如果文本以标签开头
            value = value[len(label):].strip()  # 去掉标签部分，只留值"英语"
        if label:  # 标签不为空才记录
            facts[label] = value  # 写入字典
    return facts  # 返回事实字典


def parse_jsonld(text):
    """从HTML中提取JSON-LD结构化数据（包含准确的上映日期和评分）"""
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)  # 用正则找到JSON-LD脚本块
    if not m:  # 没找到则返回空字典
        return {}  # 返回空字典表示无数据
    raw = re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.S).strip()  # 去掉/* <![CDATA[ */这类注释包裹
    try:  # 尝试解析JSON
        return json.loads(raw)  # 返回解析后的字典
    except json.JSONDecodeError:  # JSON解析失败时
        return {}  # 返回空字典兜底


def parse_movie(url):
    """抓取并解析单部电影详情页，返回包含所有字段的字典"""
    text = fetch(url)  # 下载详情页HTML
    movie = {"url": url}  # 初始化结果字典，先记录详情页地址
    if not text:  # 下载失败
        return movie  # 直接返回只有url的字典
    doc = html.fromstring(text)  # 解析成xpath文档对象
    data = parse_jsonld(text)  # 解析JSON-LD数据
    facts = parse_facts(doc)  # 解析左侧事实栏

    # ---------- 电影名 ----------
    title = doc.xpath('//section[contains(@class,"header")]//h2/a[1]/text()')  # 详情页大标题下的电影名
    movie["电影名"] = title[0].strip() if title else data.get("name", "")  # 优先用页面标题，缺失时用JSON-LD的name

    # ---------- 年份 ----------
    year = doc.xpath('//span[contains(@class,"release_date")]/text()')  # 标题旁的年份，格式如"(1994)"
    movie["年份"] = year[0].strip("() ") if year else ""  # 去掉括号只留年份数字

    # ---------- 上映时间 ----------
    events = data.get("releasedEvent") or []  # JSON-LD中的上映事件列表（原始上映日期，最准确）
    dates = [e.get("startDate", "") for e in events if e.get("startDate")]  # 提取所有上映日期
    movie["上映时间"] = min(dates) if dates else ""  # 取最早的日期作为上映时间，如"1994-09-23"

    # ---------- 类型 ----------
    genres = doc.xpath('//span[@class="genres"]//a/text()')  # 标题下方的类型链接文字，如["剧情","犯罪"]
    movie["类型"] = "、".join(g.strip() for g in genres)  # 用中文顿号连接成"剧情、犯罪"

    # ---------- 时长 ----------
    runtime = doc.xpath('//span[@class="runtime"]/text()')  # 时长文本，如"2h 22m"
    movie["时长"] = runtime[0].strip() if runtime else data.get("duration", "")  # 缺失时用JSON-LD的duration兜底

    # ---------- 评分 ----------
    rating = (data.get("aggregateRating") or {}).get("ratingValue")  # JSON-LD中的精确评分，如8.731
    if rating is None:  # JSON-LD中没有评分时
        percent = doc.xpath('//div[contains(@class,"user_score_chart")]/@data-percent')  # 从评分圆环取百分比，如"87"
        rating = float(percent[0]) / 10 if percent else ""  # 把87换算成8.7
    movie["评分"] = rating  # 记录评分

    # ---------- 语言 ----------
    lang = ""  # 先初始化为空串
    for k, v in facts.items():  # 遍历事实栏字典
        if "语言" in k or "language" in k.lower():  # 找到标签是"默认语言"或"Original Language"的项
            lang = v  # 取它的值，如"英语"
            break  # 找到即退出循环
    movie["语言"] = lang  # 记录语言

    # ---------- 导演 / 作者 ----------
    directors = []  # 存放导演名字的列表
    writers = []  # 存放作者名字的列表
    for li in doc.xpath('//ol[contains(@class,"people no_image")]/li[@class="profile"]'):  # 遍历页头主创人员列表
        name = li.xpath("./p[1]/a/text()")  # 取人名链接文字，如"弗兰克·德拉邦特"
        name = name[0].strip() if name else ""  # 取第一个并去空白
        jobs = li.xpath('./p[@class="character"]/text()')  # 取职位文字，如"Director, Screenplay"
        jobs = jobs[0].lower() if jobs else ""  # 转小写方便关键词匹配
        if not name:  # 人名为空则跳过
            continue  # 处理下一个人
        if "director" in jobs:  # 职位包含"director"（导演）
            directors.append(name)  # 加入导演列表
        if any(w in jobs for w in WRITER_JOBS):  # 职位包含任一作者关键词（编剧/原著小说等）
            writers.append(name)  # 加入作者列表
    movie["导演"] = "、".join(directors)  # 多个导演用顿号连接
    movie["作者"] = "、".join(writers)  # 多个作者用顿号连接

    # ---------- 主演 ----------
    cast = doc.xpath('//section[contains(@class,"top_billed")]//ol[contains(@class,"people scroller")]/li[contains(@class,"card")]/p[1]/a/text()')  # 顶部主演区所有演员名
    movie["主演"] = "、".join(c.strip() for c in cast if c.strip())  # 主演名用顿号连接（一般9人）

    # ---------- slogan ----------
    tagline = doc.xpath('//h3[contains(@class,"tagline")]/text()')  # 页面上的标语（slogan）
    movie["slogan"] = tagline[0].strip() if tagline else ""  # 缺失则为空串

    # ---------- 简介 ----------
    overview = doc.xpath('//div[@class="overview"]//p//text()')  # 简介段落的所有文字片段
    movie["简介"] = "".join(t.strip() for t in overview).strip()  # 拼接并去掉多余空白

    return movie  # 返回该电影的完整数据字典


def main():
    """主流程：获取链接 -> 逐部解析 -> 写入csv"""
    links = get_top100_links()  # 第一步：拿到top100的详情页链接
    print(f"共获取到{len(links)}部电影链接，开始抓取详情...")  # 打印提示

    fields = ["排名", "电影名", "年份", "上映时间", "类型", "时长", "评分", "语言", "导演", "作者", "主演", "slogan", "简介", "url"]  # csv列名
    rows = []  # 存放所有电影数据的列表
    for idx, (url, list_title) in enumerate(links, 1):  # 带序号遍历每部电影，序号即榜单排名
        print(f"[{idx}/{len(links)}] 正在抓取: {url}")  # 打印当前进度
        movie = parse_movie(url)  # 抓取并解析详情页
        movie["排名"] = idx  # 写入榜单排名
        movie["电影名"] = movie.get("电影名") or list_title  # 详情页没取到名字时用列表页标题兜底
        rows.append(movie)  # 把该电影数据加入列表
        time.sleep(0.5)  # 每部电影之间休息0.5秒，避免请求过快

    # utf-8-sig带BOM，用Excel打开中文不乱码；newline=""防止写出空行
    with open(CSV_FILE, "w", newline="", encoding="utf-8-sig") as f:  # 打开csv文件准备写入
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")  # 创建字典写入器，多余的键自动忽略
        writer.writeheader()  # 先写入表头行
        for row in rows:  # 遍历每部电影数据
            writer.writerow(row)  # 写入一行

    print(f"完成！共保存{len(rows)}部电影到 {CSV_FILE}")  # 打印完成提示


if __name__ == "__main__":  # 只有直接运行本文件时才执行主流程
    main()  # 调用主函数
