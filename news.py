import os
import urllib
from urllib.request import urlretrieve
import extractor
import datetime
import re
import pymysql
import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
from os import path
import matplotlib.pyplot as plt
from wordcloud import WordCloud,STOPWORDS,ImageColorGenerator
import pickle
import jieba
import codecs


class CollectData():
    def __init__(self):
        self.new_title = []
        self.new_time=[]
        self.new_from=[]
        self.new_time_Date=[]
        self.new_content=[]
        self.target_all_url = []
        #self.keyword1=keyword1
        print("心系联通！")

    def get_data(self,url):
        # target_url=[]
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36"}
        reponse = requests.get(url=url,
                               headers=header,
                               timeout=30
                               )
        reponse.encoding = "utf-8"
        html = reponse.text
        bf = BeautifulSoup(html, 'html5lib')
        # 找出有多少个页面


        #找出标题
        targets_url1 = bf.find_all('h3',class_="c-title")
        for target in targets_url1:
            link=target.find('a')
            self.target_all_url.append(link.get('href'))
            new_title1=link.get_text()
            self.new_title.append(new_title1.replace('\n','').replace(' ',''))

        # 找出时间和来源
        new_time_froms=bf.find_all('div',class_='c-title-author')
        for new_time_from1 in new_time_froms:
            timeAndFrom=new_time_from1.get_text().replace('\xa0','').replace('\t','')
            new_from1=timeAndFrom.split('\n')[0]
            new_time1=timeAndFrom.split('\n')[1]
            self.new_from.append(new_from1)
            self.new_time.append(new_time1)
        return self.target_all_url,self.new_title,self.new_from,self.new_time,bf

    def get_all_data(self,keyword):
        # 提取新闻第一页的内容
        year=datetime.datetime.now().year
        month=datetime.datetime.now().month
        day=datetime.datetime.now().day
        # url分析思路在txt文档中
        # url='http://news.baidu.com/ns?from=news&cl=2&bt=0&y0='+str(year)+'&m0='+str(month)+'&d0='+'&y1='+str(year)+'&m1='+str(month)+'&d1='+str(day)+'&et=0&q1='+urllib.parse.quote(keyword)+'&submit=%E7%99%BE%E5%BA%A6%E4%B8%80%E4%B8%8B&q3=&q4=&s=1&mt=24&lm=24&begin_date='+str(year)+'-'+str(month)+'-'+str(day)+'&end_date='+str(year)+'-'+str(month)+'-'+str(day)+'&tn=newstitledy&ct1=0&ct=0&rn=50&q6='
        # print(str(month),str(year),str(day),keyword)
        url = 'http://news.baidu.com/ns?from=news&cl=2&bt=0&y0=' + str(year) + '&m0=' + str(
            month) + '&d0=' + '&y1=' + str(year) + '&m1=' + str(month) + '&d1=' + str(
            day) + '&et=0&q1=' + urllib.parse.quote(keyword) + '&submit=百度一下&q3=&q4=&s=1&mt=24&lm=24&begin_date=' + str(
            year) + '-' + str(month) + '-' + str(day) + '&end_date=' + str(year) + '-' + str(month) + '-' + str(day) + '&tn=newstitledy&ct1=0&ct=0&rn=50&q6='
        self.target_all_url,self.new_title,self.new_from,self.new_time,bf=self.get_data(url)
        # 提取新闻第二页及以后的内容
        page_url=bf.find_all(class_="n")
        c = re.findall(r'rsv_page=1', str(page_url))
        page_number = 50
        while len(c)!=0:
            url = 'http://news.baidu.com/ns?word=' + urllib.parse.quote(keyword) + '&pn=' + str(page_number) + '&cl=2&ct=0&tn=newstitledy&rn=50&ie=utf-8&bt=0&et=0&lm=24'
            self.target_all_url, self.new_title, self.new_from, self.new_time,bf = self.get_data(url)
            page_number += 50
            page_url=bf.find_all(class_="n")
            c=re.findall(r'rsv_page=1',str(page_url))
        # 提取新闻正文
        for each_url in self.target_all_url:
            try:
                self.new_content.append(extractor.Extractor(url=each_url, blockSize=5, image=False).getContext())
            except Exception as e:
                print(e)
                self.new_content.append("None")
        self.new_time_Date=self.changeTime(self.new_time)
        # print(self.new_title)
        # print(self.new_from)
        # print(self.new_time)
        # print(self.target_all_url)
        # print(self.new_content)
        self.to_DB()
        self.to_excel('baidu_news'+str(datetime.datetime.now().month)+str(datetime.datetime.now().day)+'.xls')

    def changeTime(self,new_time):
        time1 = []
        for time in new_time:
            if len(re.findall(r'[0-9]+分钟前', time)) != 0:
                t = re.findall(r'[0-9]+', time)
                time1.append((datetime.datetime.now() - datetime.timedelta(minutes=int(t[0]))).strftime("%Y-%m-%d %H:%M"))
                # print((datetime.datetime.now() - datetime.timedelta(minutes=int(t[0]))).strftime("%Y-%m-%d %H:%M"))
            elif len(re.findall(r'[0-9]+小时前', time)) != 0:
                h = re.findall(r'[0-9]+', time)
                time1.append((datetime.datetime.now() - datetime.timedelta(hours=int(h[0]))).strftime("%Y-%m-%d %H:%M"))
                # print((datetime.datetime.now() - datetime.timedelta(hours=int(h[0]))).strftime("%Y-%m-%d %H:%M"))
            else:
                y = re.findall(r'[0-9]+年', time)
                y1 = re.findall(r'[0-9]+', y[0])
                m = re.findall(r'[0-9]+月', time)
                m1 = re.findall(r'[0-9]+', m[0])
                d = re.findall(r'[0-9]+日', time)
                d1 = re.findall(r'[0-9]+', d[0])
                mi = re.findall(r'[0-9]+:', time)
                mi1 = re.findall(r'[0-9]+', mi[0])
                s = re.findall(r':[0-9]+', time)
                s1 = re.findall(r'[0-9]+', s[0])
                t = y1[0] + "-" + m1[0] + "-" + d1[0] + " " + mi1[0] + ":" + s1[0]
                time1.append(t)
        return time1
    # 存到数据库中
    def to_DB(self):
        conn = pymysql.Connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='new_baidu',
            charset='utf8mb4')
        cursor = conn.cursor()
        sql = "insert into news_info(new_title,new_from,new_time,new_url,new_content) VALUES (%s,%s,%s,%s,%s);"
        for i in range(0,len(self.new_title)):
            param=(self.new_title[i], self.new_from[i], self.new_time_Date[i],self.target_all_url[i],self.new_content[i])
            try:
                cursor.execute(sql, param)
                if i%50==0:
                    conn.commit()
            except Exception as e:
                print(e)

        conn.commit()
        cursor.close()
        conn.close()
# 存到excel表中
    def to_excel(self, excel_path):
        news_dict = {'新闻标题': self.new_title, '新闻来源网站': self.new_from, '发稿时间': self.new_time_Date,
                     '新闻链接': self.target_all_url, '新闻正文': self.new_content}
        news_df = pd.DataFrame(news_dict)
        excel_writer = pd.ExcelWriter(excel_path)
        news_df.to_excel(excel_writer, index=False)
        excel_writer.save()

    #分词并生成云图
    def cloud(self):
        allcontent=''
        text=''
        allcontent=' '.join([str(i) for i in self.new_content])
        #print(allcontent)

        text += ' '.join(jieba.cut(allcontent))
        text += ' '
        fout = open('text.txt', 'wb')
        pickle.dump(text, fout)
        fout.close()
        fr = open('text.txt', 'rb')
        text = pickle.load(fr)
        # print(text)
        print("加载成功")
        backgroud_Image = plt.imread('black.jpg')
        print('加载图片成功！')
        # '''设置词云样式'''
        wc = WordCloud(
            background_color='white',
            mask=backgroud_Image,
            #font_path='C:\Windows\Fonts\STZHONGS.TTF',  # 若是有中文的话，这句代码必须添加，不然会出现方框，不出现汉字
            font_path='C:\Windows\Fonts\simsun.ttc',
            max_words=2000,
            stopwords=STOPWORDS,
            max_font_size=150,
            random_state=30
        )
        wc.generate_from_text(text)
        print('开始加载文本')
        img_colors = ImageColorGenerator(backgroud_Image)
        wc.recolor(color_func=img_colors)
        plt.imshow(wc)
        plt.axis('off')
        plt.savefig('./result2.png')
        plt.show()

        print('display success!')

    # def delete_DB(self):


    def to_DB2(self):
        conn = pymysql.Connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='new_baidu',
            charset='utf8mb4')
        cursor = conn.cursor()
        sql1='truncate table news_info1'
        cursor.execute(sql1)

        sql = "insert into news_info1(new_title,new_from,new_time,new_url,new_content) VALUES (%s,%s,%s,%s,%s);"
        for i in range(0, len(self.new_title)):
            param = (
            self.new_title[i], self.new_from[i], self.new_time_Date[i], self.target_all_url[i], self.new_content[i])
            try:
                cursor.execute(sql, param)
                if i % 50 == 0:
                    conn.commit()
            except Exception as e:
                print(e)

        conn.commit()
        cursor.close()
        conn.close()

        # # 存到excel表中
        # def to_excel(self, excel_path):
        #     news_dict = {'新闻标题': self.new_title, '新闻来源网站': self.new_from, '发稿时间': self.new_time_Date,
        #                  '新闻链接': self.target_all_url, '新闻正文': self.new_content}
        #     news_df = pd.DataFrame(news_dict)
        #     excel_writer = pd.ExcelWriter(excel_path)
        #     news_df.to_excel(excel_writer, index=False)
        #     excel_writer.save()

    # 自启动
    def timing(self,keyword):
        while True:
            now=datetime.datetime.now()
            if now.hour==9 and now.minute==5:
                break
            time.sleep(20)
        self.get_all_data(keyword)
        # self.to_DB(keyword)
        time.sleep(300)


if __name__ == "__main__":
    start = time.clock()

    keyword = input("请输入查询的关键词：")
    # hour=input("请输入自启动时间（0-24）:")
    newData = CollectData()
    newData.get_all_data(keyword)
    # newData.to_DB()
    # newData.cloud()
    #newData.timing(keyword)
    end = time.clock()
    print('程序执行了：%ds' % (end - start))