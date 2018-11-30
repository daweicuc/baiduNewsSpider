import pymysql
from dbconn import *
import json
from os import path
import matplotlib.pyplot as plt
from wordcloud import WordCloud,STOPWORDS,ImageColorGenerator
import pickle
import jieba
import codecs
from news import CollectData

class DBUtil:
    def __init__(self):
        print('constructor')

    #获取连接
    def get_conn(self):
        conn = pymysql.Connect(host=HOST,
                               port=PORT,
                               user=USER,
                               passwd=PASSWORD,
                               db=DBNAME,
                               charset=CHARSET)
        return conn


    #获取数据库信息（标题，时间，来源）
    def get_all_news(self):
        conn = self.get_conn()
        c1 = conn.cursor()
        c1.execute('SELECT new_title, new_from, new_time FROM news_info')
        rs = c1.fetchall()
        new_title_list = []
        new_from_list = []
        new_time_list=[]
        for new in rs:
            new_title_list.append(new[0])
            new_from_list.append(new[1])
            new_time_list.append(new[2])
        new_dict = {'title': new_title_list,
                     'from': new_from_list,
                     'time':new_time_list}
        new_json = json.dumps(new_dict)
        c1.close()
        conn.close()
        return new_json

    #获取时间折线图数据
    def get_num(self):
        conn = self.get_conn()
        c1 = conn.cursor()
        new_num_list = []
        for i in range(10,24):
            c1.execute("SELECT count(*) FROM news_info where new_time like '% "+str(i)+":%';")
            rs1 = c1.fetchall()
            for nu in rs1:
                new_num_list.append(nu[0])
            # print(new_num_list)
        for i in range(0,10):
            c1.execute("SELECT count(*) FROM news_info where new_time like '%0"+str(i)+":%';")
            rs1 = c1.fetchall()
            for nu in rs1:
                new_num_list.append(nu[0])
        new_dict = {'new_num': new_num_list,
                    }
        print(new_dict)
        new_num_json = json.dumps(new_dict)
        c1.close()
        conn.close()
        return new_num_json

    #获取来源饼图数据
    def get_from(self):
        conn = self.get_conn()
        c1 = conn.cursor()
        top3_from=[]
        top3_count=[]

        c1.execute("SELECT COUNT(new_from) from news_info")
        sum = c1.fetchone()[0]

        c1.execute("SELECT * from view1 ORDER BY `count(*)` DESC")

        rs1=c1.fetchall()

        if len(rs1)>3:
            rs2=rs1[0:3]
        else:
            rs2=rs1

        for nu in rs2:
            top3_from.append(nu[0])
            top3_count.append(nu[1])

        if len(rs1)>=3:
            top3_from.append('其他')
            other_count = sum - top3_count[0] - top3_count[1] - top3_count[2]
            top3_count.append(other_count)
        # elif len(rs1)==2:
        #     top3_from.append('其他1')
        #     other_count=sum-top3_count[0]-top3_count[1]
        #     top3_count.append(other_count)
        # else:
        #     top3_from.append('其他1')
        #     top3_from.append('其他2')
        #     other_count = sum - top3_count[0]
        #     top3_count.append(other_count)

        print(top3_count)
        print(top3_from)

        top3_dict={'from':top3_from,
                   'count':top3_count
        }
        top3_json = json.dumps(top3_dict)
        c1.close()
        conn.close()
        return top3_json

    #获取联通占比
    def unicom(self):
        conn = self.get_conn()
        c1 = conn.cursor()
        c1.execute("SELECT count(new_content) from news_info WHERE new_content like '%联通%'")

        count_unicom=c1.fetchone()[0]
        c1.execute("SELECT COUNT(new_from) from news_info")
        count_sum=c1.fetchone()[0]
        count_unu=count_sum-count_unicom
        percent_dict={'unicom':count_unicom,
                      'un_unicom':count_unu}
        unicom_json = json.dumps(percent_dict)
        return unicom_json

    #获取冬奥会合作伙伴对比数据
    # def partner(self):
    #     pass

    #获取新闻正文
    def get_content(self,title):
        conn = self.get_conn()
        c1 = conn.cursor()
        c1.execute('SELECT new_content from news_info where new_title=%s;', title)
        rs = c1.fetchall()
        new_content_list = []
        for content in rs:
            new_content_list.append(content[0])
        content_dict={
               'content':new_content_list
                    }
        c1.close()
        conn.close()
        return content_dict

    #获取词云图
    def get_cloud(self):
        conn = self.get_conn()
        c1 = conn.cursor()
        c1.execute('SELECT new_content from news_info')
        rs = c1.fetchall()
        new_content_list=[]
        for content in rs:
            new_content_list.append(content[0])
        allcontent = ''
        text = ''
        allcontent = ' '.join([str(i) for i in new_content_list])
        allcontent.replace('','')
        print(allcontent)
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
            # font_path='C:\Windows\Fonts\STZHONGS.TTF',  # 若是有中文的话，这句代码必须添加，不然会出现方框，不出现汉字
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

        # search页面获取时间折线图数据

    #search页面获取折线图数据
    def get_num2(self):
            conn = self.get_conn()
            c1 = conn.cursor()
            new_num_list = []
            for i in range(10, 24):
                c1.execute("SELECT count(*) FROM news_info1 where new_time like '% " + str(i) + ":%';")
                rs1 = c1.fetchall()
                for nu in rs1:
                    new_num_list.append(nu[0])
            for i in range(0, 10, 1):
                c1.execute("SELECT count(*) FROM news_info1 where new_time like '%0" + str(i) + ":%';")
                rs1 = c1.fetchall()
                for nu in rs1:
                    new_num_list.append(nu[0])
            new_dict = {'new_num': new_num_list}
            print(new_dict)
            new_num_json = json.dumps(new_dict)
            c1.close()
            conn.close()
            return new_num_json

    #search页面获取来源饼图数据
    def get_from2(self):
        conn = self.get_conn()
        c1 = conn.cursor()
        top3_from = []
        top3_count = []

        c1.execute("SELECT COUNT(new_from) from news_info1")
        sum = c1.fetchone()[0]

        c1.execute("SELECT * from view2 ORDER BY `count(new_from)` DESC")

        rs1 = c1.fetchall()

        if len(rs1) > 3:
            rs2 = rs1[0:3]
        else:
            rs2 = rs1

        for nu in rs2:
            top3_from.append(nu[0])
            top3_count.append(nu[1])

        if len(rs1) >= 3:
            top3_from.append('其他')
            other_count = sum - top3_count[0] - top3_count[1] - top3_count[2]
            top3_count.append(other_count)
        # elif len(rs1) == 2:
        #     top3_from.append('其他1')
        #     other_count = sum - top3_count[0] - top3_count[1]
        #     top3_count.append(other_count)
        # else:
        #     top3_from.append('其他1')
        #     top3_from.append('其他2')
        #     other_count = sum - top3_count[0]
        #     top3_count.append(other_count)

        print(top3_count)
        print(top3_from)

        top3_dict = {'from': top3_from,
                     'count': top3_count
                     }
        top3_json = json.dumps(top3_dict)
        c1.close()
        conn.close()
        return top3_json

    #search页面获取联通占比
    def unicom2(self):
        conn = self.get_conn()
        c1 = conn.cursor()
        c1.execute("SELECT count(new_content) from news_info1 WHERE new_content like '%联通%'")

        count_unicom=c1.fetchone()[0]
        c1.execute("SELECT COUNT(new_from) from news_info1")
        count_sum=c1.fetchone()[0]
        count_unu=count_sum-count_unicom
        percent_dict={'unicom':count_unicom,
                      'un_unicom':count_unu}
        unicom_json = json.dumps(percent_dict)
        return unicom_json

    #search页面获取正文
    def get_content2(self,title):
        conn = self.get_conn()
        c1 = conn.cursor()
        c1.execute('SELECT new_content from news_info1 where new_title=%s;', title)
        rs = c1.fetchall()
        new_content_list = []
        for content in rs:
            new_content_list.append(content[0])
        content_dict = {
            'content': new_content_list
        }
        c1.close()
        conn.close()
        return content_dict

    # 获取数据库信息（标题，时间，来源）
    def get_all_news2(self):
        conn = self.get_conn()
        c1 = conn.cursor()
        c1.execute('SELECT new_title, new_from, new_time FROM news_info')
        rs = c1.fetchall()
        new_title_list = []
        new_from_list = []
        new_time_list = []
        for new in rs:
            new_title_list.append(new[0])
            new_from_list.append(new[1])
            new_time_list.append(new[2])
        new_dict = {'title': new_title_list,
                    'from': new_from_list,
                    'time': new_time_list}
        new_json = json.dumps(new_dict)
        c1.close()
        conn.close()
        return new_json




if __name__ == '__main__':
    mysql = DBUtil()
    # new_json = mysql.get_all_news()
    mysql.get_num2()
    # mysql.unicom()
   # mysql.get_cloud()


