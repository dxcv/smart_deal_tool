#-*- coding: utf-8 -*-
import os
import sys
import datetime
import traceback
from datetime import datetime
import tushare as ts
from markdown_writer import MarkdownWriter
from markdown_table import MarkdownTable

class CDoc:
    def __init__(self, fpath_dir):
        self.sdir = fpath_dir

    def generate(self):
        index_df = ts.get_index()
        index_df = index_df[index_df.code.isin(['000001', '000016', '000300', '000905', '399001', '399006'])]
        index_df = index_df[['code', 'name', 'change', 'volume', 'amount']]
        index_df = index_df.reset_index(drop = True)

        file_name = os.path.join(self.sdir, "%s-StockReView.md" % datetime.now().strftime('%Y-%m-%d'))
        f = open(file_name, "w+")

        md = MarkdownWriter()
        ### HEADER ###
        md.addHeader("股票复盘", 1)

        ### SHOW TABEL ###
        md.addHeader("指数行情", 2)
        t = MarkdownTable(headers = ["代码","名称","涨幅(百分比)","成交量","成交额(亿)"])
        for index in range(len(index_df)):
            data_list = index_df.loc[index].tolist()
            data_list = [str(i) for i in data_list]
            t.addRow(data_list)
        md.addTable(t)

        md.addHeader("情绪变化:", 2)
        md.addImage("emotion.png", imageTitle = "今日情绪")

        md.addHeader("行业板块:", 2)
        md.addImage("industry.png", imageTitle = "行业板块")

        md.addHeader("涨跌统计:", 2)
        md.addImage("static.png", imageTitle = "涨跌统计")

        #市场的资金情况，包括融资融券占比，创业板占比

        #个股逆大盘的指数分析，融资融券的数据，

        #融资融券的数据

        #港股通的数据

        f.write(md.getStream())
        f.close()
 
if __name__ == '__main__':
    try:
        doc = CDoc()
    except Exception as e:
        traceback.print_exc()  
        sys.exit(0)