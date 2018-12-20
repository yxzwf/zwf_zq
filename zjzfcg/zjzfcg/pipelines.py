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
        insert_sql = 'insert into test_ti_tender_detail_day(' \
                     'date_id,' \
                     'prjct_name,' \
                     'prjct_code,' \
                     'prjct_desc,' \
                     'prvnce_name,' \
                     'latn_name,' \
                     'county_name,' \
                     'release_time,' \
                     'begin_time,' \
                     'end_time,' \
                     'tender_unit,' \
                     'contactor,' \
                     'contact_phone,' \
                     'purchase_money,' \
                     'agent_unit,' \
                     'agent_contactor,' \
                     'agent_phone,' \
                     'bidder_req,' \
                     'tender_note,' \
                     'open_note,' \
                     'inter_name,' \
                     'website,' \
                     'crawler_time,' \
                     'tender_detail' \
                     ') values (' \
                     '"%s","%s","%s","%s",' \
                     '"%s","%s","%s","%s","%s",' \
                     '"%s","%s","%s","%s","%s",' \
                     '"%s","%s","%s","%s","%s",' \
                     '"%s","%s","%s","%s","%s");'
        item = (item["date_id"],
                                         item["prjct_name"],
                                         re.findall('(?i)(?<=编号:|编号：)([^\'|、|采|二]*)',item["prjct_code"]),
                                         item["prjct_desc"],
                                         item["prvnce_name"],
                                         item["latn_name"],
                                         item["county_name"],
                                         item["release_time"],
                                         item["begin_time"],
                                         re.findall('(?i)(?<=:20|：20|于20|时间:|时间：)([^ |，|,|\'|日]*)',''.join(re.split("'",item["end_time"])).replace(' ','')),
                                         re.findall('(?i)(?<=:|：)([^ |，|,|3`]*)',''.join(re.split("'",item["tender_unit"]))),
                                         re.findall('(?i)(?<=人:|人：)([^ |,|，|联|(]*)',''.join(re.split("'",item["contactor"])).replace(' ', '')),
                                         re.findall('(?i)(?<=话:|话：)([^ |联|，|,|。|；]*)',''.join(re.split("'",item["contact_phone"])).replace(' ', '')),
                                         item["purchase_money"],
                                         re.findall('(?i)(?<=名称：|机构：|名称:|机构:)([^ |，|联|2]*)',''.join(re.split("'",item["agent_unit"]))),
                                         re.findall('(?i)(?<=人:|人：)([^ |,|，|联|(]*)',''.join(re.split("'",item["agent_contactor"])).replace(' ', '')),
                                         re.findall('(?i)(?<=话:|话：)([^ |联|，|,|。|传|；]*)',''.join(re.split("'",item["agent_phone"])).replace(' ', '')),
                                         item["bidder_req"].replace(' ',''),
                                         item["tender_note"].replace(' ',''),
                                        (item["open_note"].replace(' ','')).replace(' ',''),
                                         item["inter_name"],
                                         item["website"],
                                         item["crawler_time"],
                                         item["tender_detail"]
                                         )
        tx.execute(insert_sql,item)

class MysqlPipeline(object):
    #采用同步的机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect(host= mysql_host, port=mysql_port,user=mysql_user, passwd=mysql_passwd, db=mysql_db, charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()
        self.primary_key = 1000000000

    def process_item(self, item, spider):


        insert_sql = 'insert into test_ti_tender_detail_day(' \
                     'date_id,' \
                     'prjct_name,' \
                     'prjct_code,' \
                     'prjct_desc,' \
                     'prvnce_name,' \
                     'latn_name,' \
                     'county_name,' \
                     'release_time,' \
                     'begin_time,' \
                     'end_time,' \
                     'tender_unit,' \
                     'contactor,' \
                     'contact_phone,' \
                     'purchase_money,' \
                     'agent_unit,' \
                     'agent_contactor,' \
                     'agent_phone,' \
                     'bidder_req,' \
                     'tender_note,' \
                     'open_note,' \
                     'inter_name,' \
                     'website,' \
                     'crawler_time,' \
                     'tender_detail' \
                     ') values (' \
                     '"%s","%s","%s","%s",' \
                     '"%s","%s","%s","%s","%s",' \
                     '"%s","%s","%s","%s","%s",' \
                     '"%s","%s","%s","%s","%s",' \
                     '"%s","%s","%s","%s","%s");'

        self.cursor.execute(insert_sql,(item["date_id"],
                                         item["prjct_name"],
                                         re.findall('(?i)(?<=编号:|编号：)([^\'|、|采|二]*)',item["prjct_code"]),
                                         item["prjct_desc"],
                                         item["prvnce_name"],
                                         item["latn_name"],
                                         item["county_name"],
                                         item["release_time"],
                                         item["begin_time"],
                                         re.findall('(?i)(?<=:20|：20|于20|时间:|时间：)([^ |，|,|\'|日]*)',(item["end_time"].replace(' ',''))),
                                         re.findall('(?i)(?<=:|：|位)([^ |\']*)',''.join(re.split("'",item["tender_unit"]))),
                                         re.findall('(?i)(?<=系人:|系人：|方式：|联系人)([^ |联|，|电|；|,]*)',''.join(re.split("'",item["contactor"]))),
                                         re.findall('(?i)(?<=电话:|电话：|系方式)([^ |，|联]*)',''.join(re.split("'",item["contact_phone"]))),
                                         item["purchase_money"],
                                         re.findall('(?i)(?<=名称：|机构：)([^ |，|联]*)',''.join(re.split("'",item["agent_unit"]))),
                                         re.findall('(?i)(?<=人：|名：|人:|名:)([^ |电]*)',''.join(re.split("'",item["agent_contactor"]))),
                                         re.findall('(?i)(?<=话：|话:)([^ |传|;|；]*)',''.join(re.split("'",item["agent_phone"]))),
                                         item["bidder_req"].replace(' ',''),
                                         item["tender_note"].replace(' ',''),
                                        (item["open_note"].replace(' ','')).replace(' ',''),
                                         item["inter_name"],
                                         item["website"],
                                         item["crawler_time"],
                                         item["tender_detail"]
                                         ))


        # self.primary_key += 1
        self.conn.commit()
