# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


from zjzfcg.settings import mongo_host,mongo_port,mongo_db_name,mongo_db_collection_cj,mongo_db_collection_zb
from zjzfcg.settings import mysql_host,mysql_port,mysql_user,mysql_passwd,mysql_db
import  re
import MySQLdb
from twisted.enterprise import adbapi
#
# class ZjzfcgPipeline(object):
#
#     def __init__(self):
#         host = mongo_host
#         port = mongo_port
#         dbname = mongo_db_name
#         sheetname = mongo_db_collection_cj
#         client = pymongo.MongoClient(host=host, port=port)
#         mydb = client[dbname]
#         self.post = mydb[sheetname]
#
#
#     def process_item(self, item, spider):
#         data = dict(item)
#         self.post.insert(data)
#         return item
#
#


class MysqlPipeline_aio(object):
    def open_spider(self,spider):
        self.dbpool = adbapi.ConnectionPool('MySQLdb',host= mysql_host, port=mysql_port,user=mysql_user, passwd=mysql_passwd, db=mysql_db, charset="utf8",use_unicode=True)
        # self.primary_key = 1000000000
    def close_spider(self,spider):
        self.dbpool.close()
    def process_item(self,item,spider):
        self.dbpool.runInteraction(self.insert,item)

    def insert(self,tx,item):
        # self.primary_key += 1
        insert_sql = 'insert into test_ti_winbidder_detail_day(' \
                     'date_id,' \
                     'prjct_name,' \
                     'prjct_code,' \
                     'prvnce_name,' \
                     'latn_name,' \
                     'county_name,' \
                     'release_time,' \
                     'tender_unit,' \
                     'contactor,' \
                     'contact_phone,' \
                     'agent_unit,' \
                     'agent_contactor,' \
                     'agent_phone,' \
                     'winbidder_unit,' \
                     'winbidder_money,' \
                     'begin_time,' \
                     'bid_time,' \
                     'bid_month,' \
                     'inter_name,' \
                     'website,' \
                     'winbidder_detail' \
                     ') values (' \
                     '"%s","%s","%s","%s","%s",' \
                     '"%s","%s","%s","%s","%s",' \
                     '"%s","%s","%s","%s","%s",' \
                     '"%s","%s","%s","%s","%s",' \
                     '"%s");'
        item = (item["date_id"],
                                         # self.primary_key,
                                         item["prjct_name"],
                                         re.findall('(?i)(?<=编号:|编号：)([^\'|、|采|二|四]*)', item["prjct_code"].replace(' ','')),
                                         item["prvnce_name"],
                                         item["latn_name"],
                                         item["county_name"],
                                         re.findall('(?i)(?<=:|：)([^ ]*)',item["release_time"].replace(' ','')),
                                         re.findall('(?i)(?<=:|：)([^ |2|1|3|,]*)', item["tender_unit"].replace(' ','')),
                                         re.search('(?i)(?<=人:|人：)([^ |,|，|联]*)',''.join(re.split("'", item["contactor"].replace("\xa0", ""))).replace(' ', '')).group(),
                                         re.search('(?i)(?<=话:|话：)([^ |联|，|,|。]*)',''.join(re.split("'", item["contact_phone"])).replace(' ', '')).group(),
                                         re.findall('(?i)(?<=:|：|；)([^ ]*)',item["agent_unit"].replace(' ','')),
                                         re.search('(?i)(?<=人:|人：)([^ |,|，|联]*)',''.join(re.split("'", item["agent_contactor"])).replace(' ', '')).group(),
                                         re.search('(?i)(?<=话:|话：)([^ |联|，|,]*)',''.join(re.split("'", item["agent_phone"])).replace(' ', '')).group(),
                                         item["winbidder_unit"],
                                         item["winbidder_money"],
                                         re.findall('(?i)(?<=:|：)([^ ]*)',item["begin_time"].replace(' ','')),
                                         re.findall('(?i)(?<=:|：)([^ ]*)',item["bid_time"].replace(' ','')),
                                         re.findall('(?i)(?<=:|：)([^ ]*)',item["bid_month"].replace(' ','')),
                                         item["inter_name"],
                                         item["website"],
                                         item["winbidder_detail"]
                                         )
        tx.execute(insert_sql,item)


class MysqlPipeline(object):
    #采用同步的机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect(host= mysql_host, port=mysql_port,user=mysql_user, passwd=mysql_passwd, db=mysql_db, charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()
        # self.primary_key = 1000000000

    def process_item(self, item, spider):


        insert_sql = 'insert into test_ti_winbidder_detail_day(' \
                     'date_id,' \
                     'prjct_name,' \
                     'prjct_code,' \
                     'prvnce_name,' \
                     'latn_name,' \
                     'county_name,' \
                     'release_time,' \
                     'tender_unit,' \
                     'contactor,' \
                     'contact_phone,' \
                     'agent_unit,' \
                     'agent_contactor,' \
                     'agent_phone,' \
                     'winbidder_unit,' \
                     'winbidder_money,' \
                     'begin_time,' \
                     'bid_time,' \
                     'bid_month,' \
                     'inter_name,' \
                     'website,' \
                     'winbidder_detail' \
                     ') values (' \
                     '"%s","%s","%s","%s","%s",' \
                     '"%s","%s","%s","%s","%s",' \
                     '"%s","%s","%s","%s","%s",' \
                     '"%s","%s","%s","%s","%s",' \
                     '"%s");'

        self.cursor.execute(insert_sql,(item["date_id"],
                                         # self.primary_key,
                                         item["prjct_name"],
                                         re.findall('(?i)(?<=编号:|编号：)([^\'|、|采|二|四]*)', item["prjct_code"].replace(' ','')),
                                         item["prvnce_name"],
                                         item["latn_name"],
                                         item["county_name"],
                                         re.search('(?i)(?<=:|：)([^ ]*)',item["release_time"].replace(' ','')),
                                         re.search('(?i)(?<=:|：)([^ |2|1|3|,]*)', item["tender_unit"].replace(' ','')),
                                         re.search('(?i)(?<=人:|人：)([^ |,|，|联]*)',''.join(re.split("'",item["contactor"].replace("\xa0",""))).replace(' ','')).group(),
                                         re.search('(?i)(?<=话:|话：)([^ |联|，|,]*)',''.join(re.split("'", item["contact_phone"])).replace(' ', '')).group(),
                                         re.search('(?i)(?<=:|：)([^ ]*)',item["agent_unit"].replace(' ','')),
                                         re.search('(?i)(?<=人:|人：)([^ |,|，|联]*)',''.join(re.split("'",item["agent_contactor"])).replace(' ','')).group(),
                                         re.search('(?i)(?<=话:|话：)([^ |联|，|,]*)',''.join(re.split("'",item["agent_phone"])).replace(' ','')).group(),
                                         item["winbidder_unit"],
                                         item["winbidder_money"],
                                         re.search('(?i)(?<=:|：)([^ ]*)',item["begin_time"].replace(' ','')),
                                         re.search('(?i)(?<=:|：)([^ ]*)',item["bid_time"].replace(' ','')),
                                         re.search('(?i)(?<=:|：)([^ ]*)',item["bid_month"].replace(' ','')),
                                         item["inter_name"],
                                         item["website"],
                                         item["winbidder_detail"],
                                         ))


        # self.primary_key += 1
        self.conn.commit()
