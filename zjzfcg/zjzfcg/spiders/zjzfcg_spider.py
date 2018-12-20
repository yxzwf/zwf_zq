# -*- coding: utf-8 -*-
import scrapy
import re
from zjzfcg.items import ZjzfcgItem
import json
import random
import datetime
class ZjzfcgSpiderSpider(scrapy.Spider):
    name = 'zjzfcg_spider'
    allowed_domains = ['zjzfcg.gov.cn']
    primary_key = 1

    def citycode_cityname_dict(self):
        my_dict = {}
        my_dict['330199'] = '杭州市'
        my_dict['330299'] = '宁波市'
        my_dict['330399'] = '温州市'
        my_dict['330499'] = '嘉兴市'
        my_dict['330599'] = '湖州市'
        my_dict['330699'] = '绍兴市'
        my_dict['330799'] = '金华市'
        my_dict['330899'] = '衢州市'
        my_dict['330999'] = '舟山市'
        my_dict['331099'] = '台州市'
        my_dict['331199'] = '丽水市'
        my_dict['339900'] = '浙江'
        return my_dict






    def start_requests(self):
        #http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=15&pageNo=1&noticeType=2&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch&pubDate=2018-01-01+&endDate=2018-04-01+&isExact=1
        # yield scrapy.Request('http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=15&pageNo=1&noticeType=10&url=http://notice.zcy.gov.cn/new/noticeSearch',callback=self.parse)

        start_urls = []
        for city_code in ['330199','330299','330399','330499','330599','330699','330799','330899','330999','331099','331199','339900']:
            for i in range(100):
                i = i+1
                start_url='http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=15&pageNo='+str(i)+'&noticeType=2&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch&pubDate=2018-11-01+&endDate=2018-12-18+&isExact=1&district='+city_code

                yield scrapy.Request(start_url,meta={'cityCode':city_code} ,callback=self.parse)

    def parse(self, response):
        #此列表页中解析所有的url

        # print(json.loads(response.text)['articles'][1]['url'])
        cityCode = response.meta.get("cityCode")
        for article in json.loads(response.text)['articles']:
            disticode = article['districtName']
            origin_url = article['url']
            process_url = origin_url.replace("innerUsed_noticeDetails/index.html","cms/api/cors/getRemoteResults") + "&url=http://notice.zcy.gov.cn/new/noticeDetail"
            # print(process_url)
            yield scrapy.Request(process_url,meta={'disticode':disticode,'cityCode':cityCode},callback=self.detail_parse)

    def detail_parse(self,response):
        tendering = ZjzfcgItem()

        disticode = response.meta.get('disticode')
        tendering['county_name'] = disticode

        tendering['date_id'] = int(datetime.datetime.now().strftime("%Y%m%d"))
        prjct_name = response.xpath('//*[contains(text(),"noticeTitle")]/text()').re('(?i)(?<="noticeTitle":")([^","]*)')
        tendering['prjct_name'] = prjct_name if prjct_name else ""
        prjct_code = response.css('p:contains("项目编号") ::text,'
                                  'p:contains("项目编号")+p:contains("-") ::text,'
                                  'h2:contains("项目编号")+p:contains("-") ::text,'
                                  'p:contains("采购编号") ::text,'
                                  'p:contains("招标编号") ::text,'
                                  'p:contains("询价编号") ::text,'
                                  'td:contains("招标编号") ::text,'
                                  'p:contains(编号：) ::text,'
                                  'p:contains(项目名称及编号) ::text,'
                                  'tr:contains(项目编号) ::text')
        tendering['prjct_code'] = ((''.join(prjct_code.extract())).replace(' ','')) if prjct_code else ""
        prjct_desc = response.css('p:contains(中华人民共和国政府采购法):contains(项目进行) ::text,'
                                  'p:contains(武警浙江总队物资采购实施细则) ::text')
        tendering['prjct_desc'] = ''.join(prjct_desc.extract()) if prjct_desc else ""
        tendering['prvnce_name'] = '浙江省'


        # if "district=" in response.url:
        #     print('======')
        #     print(response.url)
        #
        #     tmp_disic = response.url.split("district=")[1]
        #     tmp_disic_num = tmp_disic.split("&")[0] if "&" in tmp_disic else tmp_disic
        #     print(tmp_disic_num)
        #     distic_dict = self.citycode_cityname_dict()
        #     print(distic_dict[tmp_disic_num])
        #     tendering['latn_name'] = disticode[tmp_disic_num]
        # else:
        distic_dict = self.citycode_cityname_dict()
        tendering['latn_name'] = distic_dict[response.meta.get('cityCode')]
        release_time = response.xpath("//*[contains(text(),'noticePubDate')]/text()").re('\d{4}-\d{2}-\d{2}')[0]
        tendering['release_time'] = release_time if release_time else ""
        begin_time = response.xpath('//*[contains(text(),"noticePubDate")]/text()').re('\d{4}-\d{2}-\d{2}')[0]
        tendering['begin_time'] = begin_time if begin_time else ""
        end_time = response.css('p:contains(投标截止时间) ::text,'
                                'p:contains(投标截止时间)+p:contains(年):contains(月) ::text,'
                                'h2:contains(投标截止时间)+p:contains(年):contains(月) ::text,'
                                'p:contains(递交截止时间)+p:contains(年):contains(月):contains(日) ::text,'
                                'p:contains(提交截止时间) ::text,'
                                'p:contains(提交截止时间)+p:contains(年):contains(月) ::text,'
                                'p:contains(磋商截止时间) ::text,'
                                'p:contains(磋商截止时间)+p:contains(年):contains(月) ::text,'
                                'p:contains(开标时间)+p:contains(年):contains(月) ::text')
        tendering['end_time'] = ''.join(end_time.extract()) if end_time else ""
        tender_unit = response.css('p:contains("采购单位:") ::text,'
                                   'tr:contains(采购单位) ::text,'
                                   'p:contains("采购单位：") ::text,'
                                   'p:contains("采购人名称") ::text,'
                                   'p:contains("招标人名称") ::text,'
                                   'p:contains("采购人：") ::text,'
                                   'p:contains("招标人：") ::text,'
                                   'p:contains(采购机构) ::text')
        tendering['tender_unit'] = ''.join(tender_unit.extract()) if tender_unit else ""
        contactor = response.css('p:contains("采购单位")+p:contains(联系人) ::text,'
                                 'tr:contains(采购单位)+tr+tr+tr:contains(联系人) ::text,'
                                 'p:contains(采购机构)+p:contains(联系人) ::text,'
                                 'p:contains("采购单位"):contains(联系人) ::text,'
                                 'p:contains("业务单位"):contains(联系人) ::text,'
                                 'p:contains(采购人名称)+p:contains(联系人) ::text,'
                                 'p:contains(采购人名称)+p+p:contains(联系人) ::text,'
                                 'p:contains("采购人：")+p+p:contains(联系人) ::text,'
                                 'p:contains(采购人名称)+p+p:contains("联 系 人") ::text,'
                                 'p:contains(采购人名称):contains(联系人) ::text,'
                                 'p:contains(采购单位)+p:contains(联系人) ::text,'
                                 'p:contains(采购单位)+p+p:contains(联系人) ::text,'
                                 'p:contains(采购单位)+p+p:contains("联 系 人") ::text,'
                                 'p:contains(招标人名称)+p:contains(联系人) ::text,'
                                 'p:contains(采购人)+p+p+p:contains(联系人) ::text,'
                                 'p:contains(采购人名称)+p:contains("联 系 人") ::text,'
                                 'p:contains(采购人名称)+p:contains(联系人) ::text,'
                                 'p:contains("招标人：")+p:contains(联系人) ::text,'
                                 'p:contains("招标人：")+p+p:contains(联系人) ::text,'
                                 'p:contains("采购人")+p:contains(联系人) ::text,'
                                 'p:contains(采购方联系方式) ::text')
        tendering['contactor'] = ''.join(contactor.extract()) if contactor else ""
        contact_phone = response.css('p:contains(采购单位)+p:contains(电话) ::text,'
                                     'p:contains(采购人名称):contains(电话) ::text,'
                                     'tr:contains(采购单位)+tr+tr+tr+tr:contains(联系方式) ::text,'
                                     'p:contains(采购方联系方式):contains(电话) ::text,'
                                     'p:contains(采购机构)+p+p:contains(电话) ::text,'
                                     'p:contains("业务单位"):contains(电话) ::text,'
                                     'p:contains("采购单位"):contains(联系电话) ::text,'
                                     'p:contains(采购人名称)+p+p:contains(电话) ::text,'
                                     'p:contains(采购人名称)+p+p+p:contains(联系电话) ::text,'
                                     'p:contains(采购人：)+p+p:contains(联系人)+p:contains(联系电话) ::text,'
                                     'p:contains(采购人名称)+p:contains(联系电话) ::text,'
                                     'p:contains(采购人名称)+p+p+p:contains(联系方) ::text,'
                                     'p:contains(招标人名称)+p+p:contains(联系电话),'
                                     'p:contains(采购单位)+p+p:contains(电话) ::text,'
                                     'p:contains(采购单位)+p:contains(电话) ::text,'
                                     'p:contains(采购单位)+p+p:contains(电话) ::text,'
                                     'p:contains("招标人：")+p:contains(联系电话) ::text,'
                                     'p:contains("招标人：")+p+p:contains(联系电话) ::text,'
                                     'p:contains(采购单位)+p+p+p:contains("电    话") ::text,'
                                     'p:contains(采购单位)+p+p+p:contains(电话) ::text,'
                                     'p:contains("招标人：")+p+p+p:contains(联系) ::text,'
                                     'p:contains("采购人")+p+p:contains(联系电话) ::text,'
                                     'p:contains("采购人")+p:contains(电话) ::text')



        tendering['contact_phone'] = ''.join(contact_phone.extract()) if contact_phone else ""

        tmp_jine = response.css("table > tbody > tr > td:contains(预算) ::text,"
                                "table > tbody > tr > th:contains(预算) ::text")
        tmp_all = response.css("table > tbody > tr:nth-child(1) ::text,"
                               "table > thead > tr:nth-child(1) ::text")
        d = response.css("p:contains(预算金额：) ::text,"
                         "p:contains(采购预算：) ::text,"
                         "p:contains(预算价：) ::text,"
                         "table > tbody > tr:nth-child(1)+tr:contains(预算) ::text,"
                         "table > thead > tr:nth-child(1)+tr:contains(预算) ::text")
        if tmp_jine :
            if tmp_all:
                jine = tmp_jine.extract_first()
                all = tmp_all.extract()
                if jine in all:
                    index = all.index(jine) + 1
                    purchase_money = response.css("table > tbody > tr:nth-child(1)+tr > td:nth-child("+str(index)+") ::text,"
                                                    "table > thead + tbody > tr:nth-child(1) > td:nth-child("+str(index)+") ::text")

                    tendering['purchase_money'] = ''.join(purchase_money.extract())+'%%%'+''.join(tmp_all.extract()) if purchase_money  else d.extract()
                else:
                    tendering['purchase_money'] = d.extract()
            else:
                tendering['purchase_money'] = d.extract()
        else:
            tendering['purchase_money'] = d.extract()
        agent_unit = response.css('p:contains(代理机构名称) ::text,'
                                  'p:contains(招标代理机构) ::text,'
                                  'p:contains(采购代理机构) ::text,'
                                  'p:contains(代理机构：) ::text,'
                                  'p:contains(采购代理公司) ::text')
        tendering['agent_unit'] = ''.join(agent_unit.extract()) if agent_unit else ""
        agent_contactor = response.css('p:contains(代理机构)+p:contains(联系人) ::text,'
                                       'p:contains(采购代理公司)+p+p+p+p:contains(联系人) ::text,'
                                       'p:contains(代理机构联系人) ::text,'
                                       'p:contains(代理机构联系电话) ::text,'
                                       'p:contains(代理机构)+p+p:contains("联 系 人") ::text,'
                                       'p:contains(代理机构)+p+p:contains(联系人) ::text,'
                                       'p:contains(采购代理机构)+p+p:contains(联系人) ::text,'
                                       'p:contains(代理机构名称)+p+p:contains("联 系 人") ::text,'
                                       'p:contains(招标代理机构)+p:contains(联系人) ::text,'
                                       'p:contains(招标代理机构)+p+p:contains(联系人) ::text,'
                                       'p:contains(代理机构联系方式)+p:contains(联系人) ::text,'
                                       'p:contains(招标代理机构)+p:contains("联 系 人") ::text')
        tendering['agent_contactor'] = ''.join(agent_contactor.extract()) if agent_contactor else ""
        agent_phone = response.css('p:contains(代理机构名称)+p:contains(联系人)+p:contains(电话) ::text,'
                                   'p:contains(采购代理公司)+p+p:contains(电话) ::text,'
                                   'p:contains(代理机构):contains(电话) ::text,'
                                   'p:contains(代理机构)+p:contains("电话") ::text,'
                                   'p:contains(代理机构名称)+p:contains(电话) ::text,'
                                   'p:contains(代理机构名称)+p+p:contains(电话) ::text,'
                                   'p:contains(代理机构)+p+p+p:contains(电话) ::text,'
                                   'p:contains(代理机构)+p+p+p:contains("电  话") ::text,'
                                   'p:contains(代理机构名称)+p+p:contains(联系人)+p:contains(联系) ::text,'
                                   'p:contains(代理机构联系方式)+p:contains(联系电话) ::text,'
                                   'p:contains(招标代理机构)+p:contains(联系人)+p:contains(联系电话) ::text,'
                                   'p:contains(招标代理机构)+p:contains("联 系 人")+p:contains(联系电话) ::text,'
                                   'p:contains(招标代理机构)+p+p+p:contains(联系) ::text')
        tendering['agent_phone'] = ''.join(agent_phone.extract()) if agent_phone else ""
        bidder_req = response.css('p:contains(资格要求)+p ::text,'
                                  'p:contains(资格要求)+p+p ::text')
        tendering['bidder_req'] = ''.join(bidder_req.extract()) if bidder_req else ""
        tender_note = response.css('p:contains(招标文件的)+p ::text,'
                                   'p:contains(招标文件的)+p+p ::text,'
                                   'p:contains(磋商文件发售)+p ::text')
        tendering['tender_note']= ''.join(tender_note.extract()) if tender_note else ""
        open_note = response.css('p:contains(开标时间) ::text,p:contains(开标地址) ::text,'
                                  'p:contains(开标时间及地点) ::text')
        tendering['open_note']= ''.join(open_note.extract()) if open_note else ""
        tendering['inter_name'] = "浙江政府采购网"
        tendering['website'] = response.url
        crawler_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        tendering['crawler_time'] = int(crawler_time)
        # tender_detail = response.xpath('//*/text()')
        jsonstr=(''.join(response.xpath('//*/text()').extract())).replace('\xa0','')
        jsonstr2 = re.sub("[^({|:|,)]\"[^(}|,|:)]", "", jsonstr)
        str2 = (json.loads(jsonstr2)).get("noticeContent")
        if "}" in str2:
            aa=str2.split("}")[1]
            if aa:
                if "附件信息" in aa:
                    tendering['tender_detail']=aa.split("附件信息")[0]
                else:
                    tendering['tender_detail']=aa
            else:
                if "附件信息" in str2:
                    tendering['winbidder_detail'] = str2.split("附件信息")[0]
                else:
                    tendering['winbidder_detail'] = str2
        else:
            if "附件信息" in str2:
                tendering['winbidder_detail'] = str2.split("附件信息")[0]
            else:
                tendering['winbidder_detail'] = str2
        # tendering['tender_detail'] = tender_detail.extract().trip() if tender_detail else ""




        yield tendering
