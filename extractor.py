#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import requests as req
import re
import urllib.request
import chardet
from bs4 import BeautifulSoup

DBUG   = 0

reBODY =re.compile( r'<body.*?>([\s\S]*?)<\/body>', re.I)
reCOMM = r'<!--.*?-->'
reTRIM = r'<{0}.*?>([\s\S]*?)<\/{0}>'
reTAG  = r'<[\s\S]*?>|[ \t\r\f\v]'

reIMG  = re.compile(r'<img[\s\S]*?src=[\'|"]([\s\S]*?)[\'|"][\s\S]*?>')

class Extractor():
    def __init__(self, url = "", blockSize=3, timeout=30, image=False):
        self.url       = url
        self.blockSize = blockSize
        self.timeout   = timeout
        self.saveImage = image
        self.rawPage   = ""
        self.ctexts    = []
        self.cblocks   = []


    def getRawPage(self):

        try:
            header = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36"}
            resp = req.get(self.url, headers=header,timeout=self.timeout)
            #print(resp.text)
            #re_text = resp.text
        except Exception as e:
            raise e
            #print(e)

        if DBUG: print(resp.encoding)
        print(resp.encoding)
        #print(resp.text)
        #print(soup)
        if resp.encoding == 'ISO-8859-1':

            try:
                #re_text = resp.text.encode('iso-8859-1').decode('utf-8')
                re_text = resp.text.encode('iso-8859-1').decode('utf-8')
                #print(re_text)

            except Exception as e:
                    print(e)
                    resp.encoding = "gb2312"
                    re_text = resp.text

        else:re_text = resp.text

        # print(resp.status_code)
        #print(re_text)

        return resp.status_code, re_text

    def processTags(self):
        self.body = re.sub(reCOMM, "", self.body)
        #print(self.body)
        self.body = re.sub(reTRIM.format("script"), "" ,re.sub(reTRIM.format("style"), "", self.body))
        # self.body = re.sub(r"[\n]+","\n", re.sub(reTAG, "", self.body))
        self.body = re.sub(reTAG, "", self.body)
        #print(self.body)

    def processBlocks(self):
        self.ctexts   = self.body.split("\n")
        #print(len(self.ctexts))
        #print(self.ctexts)
        self.textLens = [len(text) for text in self.ctexts]
        #print(self.textLens)
        if len(self.ctexts)<=3:
            result=self.ctexts
        else:
            #print('dd')
            self.cblocks  = [0]*(len(self.ctexts) - self.blockSize - 1)
            lines = len(self.ctexts)
            for i in range(self.blockSize):
                self.cblocks = list(map(lambda x,y: x+y, self.textLens[i : lines-1-self.blockSize+i], self.cblocks))
                #print(self.cblocks)

            maxTextLen = max(self.cblocks)

            if DBUG: print(maxTextLen)

            self.start = self.end = self.cblocks.index(maxTextLen)
            # print(self.end)
            # print(min(self.textLens))
            # print(self.cblocks[self.end])
            while self.start > 0 and self.cblocks[self.start] > min(self.textLens):
                self.start -= 1
            while self.end < lines - self.blockSize and self.cblocks[self.end] > min(self.textLens):
                self.end += 1

            result="".join(self.ctexts[self.start:self.end])
        #return "".join(self.ctexts[self.start:self.end])
        return result

    def processImages(self):
        self.body = reIMG.sub(r'{{\1}}', self.body)

    def getContext(self):
        code, self.rawPage = self.getRawPage()
        #print(self.rawPage)
        #print(self.body)
        #print(reBODY)
        #print(re.match(reBODY,self.rawPage))
        self.body = re.findall(reBODY, self.rawPage)[0]
        #print(self.body)

        if DBUG: print(code, self.rawPage)

        if self.saveImage:
            self.processImages()
        self.processTags()
        return self.processBlocks()
        # print(len(self.body.strip("\n")))

if __name__ == '__main__':
    ext = Extractor(url="http://www.csteelnews.com/qypd/qyzx/201811/t20181107_372268.html",blockSize=3, image=False)
    #ext=Extractor(url="http://www.dzzq.com.cn/estate/39898056.html",blockSize=5,image=False)

    #print(ext.getContext().replace("&nbsp;",""))
    print(ext.getContext())
    #print(type(ext.getContext()))