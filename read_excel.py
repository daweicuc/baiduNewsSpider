import xlrd
import json
from news import CollectData
import cgi
import re

#search.html显示结果是读baidu_news.xls的

class ReadExcel:
    def __init__(self):
        # self.keyword1=keyword1
        print('read')

    def get_search_news(self, keyword):
        data=CollectData()
        # print('get_search_news' + keyword)
        data.get_all_data(keyword)
        data.to_DB2()
        workbook=xlrd.open_workbook('baidu_news.xls',encoding_override='utf-8')
        sheets=workbook.sheets()
        sheet1=sheets[0]
        new_title_list=sheet1.col_values(0)
        del new_title_list[0]
        new_from_list=sheet1.col_values(1)
        del new_from_list[0]
        new_time_list=sheet1.col_values(2)
        del new_time_list[0]
        new_content_list=sheet1.col_values(4)
        del new_content_list[0]
        # print(new_content_list)
        new_dict={
            'title': new_title_list,
            'from': new_from_list,
            'time': new_time_list
        }
        # print(new_dict)
        new_json = json.dumps(new_dict,ensure_ascii=False)
        # print(new_json)
        return new_json

    def get_time(self):
        pass




if __name__=='__main__':
    reade=ReadExcel()
    reade.get_search_news("联通")
