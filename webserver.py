from flask import Flask, request, redirect
import json
from dbutil import DBUtil
from read_excel import ReadExcel


class WebServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        print('host:%s\tport:%d' % (self.host, self.port))

    def get_webserver(self):
        web_server = Flask(__name__, static_folder='', static_url_path='')
        return web_server

    def set_route(self, web_server):
        @web_server.route('/', methods=['GET', 'POST'])
        def index():
            print('root')
            return 'welcome'

        #获取新闻列表信息
        @web_server.route('/get_all_news', methods=['GET', 'POST'])
        def get_all_news():
            mysql = DBUtil()
            book_json = mysql.get_all_news()
            return book_json

        #在新闻列表中点击“正文”按钮得到新闻正文
        @web_server.route('/get_content', methods=['GET', 'POST'])
        def get_content():
            mysql = DBUtil()
            name = request.args.get('title')
            content_c = mysql.get_content(name)
            return content_c['content'][0]

        #获取折线图数据
        @web_server.route('/get_line', methods=['GET', 'POST'])
        def get_line():
            mysql = DBUtil()
            new_line = mysql.get_num()
            return new_line

        #获取新闻来源网站饼状图数据
        @web_server.route('/get_pie',methods=['GET','POST'])
        def get_pie():
            mysql=DBUtil()
            from_json=mysql.get_from()
            return from_json

        #获取联通占比饼状图数据
        @web_server.route('/get_unicom',methods=['GET','POST'])
        def get_unicom():
            mysql=DBUtil()
            u_json=mysql.unicom()
            return u_json

        #获取词云图
        @web_server.route('/get_cloud',methods=['GET','POST'])
        def get_cloud():
            mysql = DBUtil()
            mysql.get_cloud()

        # search页面获取前端搜索的关键词并从后端获取该关键词对应的新闻信息
        @web_server.route('/get_keyword', methods=['GET', 'POST'])
        def get_keyword():
            if request.method == 'GET':
                keyword1 = request.args.get('keyword2')
                readex = ReadExcel()
                search_json = readex.get_search_news(keyword1)
                return search_json

            else:
                keyword1 = request.form.get('keyword2')
                readex = ReadExcel()
                search_json = readex.get_search_news(keyword1)
                return search_json

        # search页面获取新闻正文
        @web_server.route('/get_content2', methods=['GET', 'POST'])
        def get_content2():
            mysql = DBUtil()
            name = request.args.get('title')
            content_c = mysql.get_content2(name)
            return content_c['content'][0]

        #search页面获取折线图数据
        @web_server.route('/get_line2', methods=['GET', 'POST'])
        def get_line2():
            mysql = DBUtil()
            new_line = mysql.get_num2()
            return new_line

        #search页面获取新闻来源饼状图数据
        @web_server.route('/get_pie2', methods=['GET', 'POST'])
        def get_pie2():
            mysql = DBUtil()
            from_json = mysql.get_from2()
            return from_json

        #seaarch页面获取联通占比饼状图数据
        @web_server.route('/get_unicom2', methods=['GET', 'POST'])
        def get_unicom2():
            mysql = DBUtil()
            u_json = mysql.unicom2()
            return u_json




if __name__ == '__main__':
    app = WebServer('0.0.0.0', 80)
    web_server = app.get_webserver()
    app.set_route(web_server)
    web_server.run(host=app.host, port=app.port, debug=True)