# -*- coding: utf-8 -*-
import scrapy

from zjzfcg.items import ZjzfcgItem
import json
import random
import datetime
import re
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
            for i in range(110):
                i = i+1
                #start_url='http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=15&pageNo='+str(i)+'&noticeType=10&url=http://notice.zcy.gov.cn/new/noticeSearch'
                start_url='http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=15&pageNo='+str(i)+'&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch&noticeType=51&pubDate=2018-11-01+&endDate=2018-12-19+&isExact=1&district='+city_code
                yield scrapy.Request(start_url,meta={'cityCode':city_code}, callback=self.parse)

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
        tendering['prvnce_name'] = '浙江省'

        distic_dict = self.citycode_cityname_dict()
        tendering['latn_name'] = distic_dict[response.meta.get('cityCode')]
        release_time=response.css('p:contains("采购公告"):contains("日期") ::text')
        tendering['release_time'] = ''.join(release_time.extract()) if release_time else ""
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
        cc=''.join(contactor.extract())
        tendering['contactor'] = cc.replace('\xa0','') if cc else ""
        print(type(tendering['contactor']))
        print(tendering['contactor'])
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
        agent_unit = response.css('p:contains(代理机构名称：) ::text,'
                                  'p:contains(招标代理机构：) ::text,'
                                  'p:contains(采购代理机构：) ::text,'
                                  'p:contains(代理机构：) ::text,'
                                  'p:contains(采购代理公司：) ::text')
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
        tendering['agent_contactor'] = (''.join(agent_contactor.extract())).replace('\xa0','') if agent_contactor else ""
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
        tmp_jine = response.css("table > tbody > tr > td:contains(供应商) ::text,"
                                "table > tbody > tr > td:contains(中标单位) ::text,"
                                "table > tbody > tr > th:contains(中标单位) ::text,"
                                "table > tbody > tr > th:contains(供应商) ::text,"
                                "table > tbody > tr > td:contains(中标人) ::text,"
                                "table > tbody > tr > th:contains(中标人) ::text")
        tmp_all = response.css("table > tbody > tr:nth-child(1) ::text,"
                               "table > thead > tr:nth-child(1) ::text")
        d = response.css("p:contains(中标人：) ::text,"
                         "p:contains(中标机构：) ::text,"
                         "p:contains(中标供应商：) ::text,"
                         "p:contains(中标单位：) ::text")
        if tmp_jine:
            if tmp_all:
                jine = tmp_jine.extract_first()
                all = tmp_all.extract()
                if jine in all:
                    index = all.index(jine) + 1
                    winbidder_unit = response.css(
                        "table > tbody > tr:nth-child(1)+tr > td:nth-child(" + str(index) + ") ::text,"
                        "table > thead + tbody > tr:nth-child(1) > td:nth-child(" + str(index) + ") ::text")

                    tendering['winbidder_unit'] = ''.join(winbidder_unit.extract()) if winbidder_unit else ''.join(d.extract())
                else:
                    tendering['winbidder_unit'] = ''.join(d.extract())
            else:
                tendering['winbidder_unit'] = ''.join(d.extract())
        else:
            tendering['winbidder_unit'] = ''.join(d.extract())

        tmp_jin = response.css("table > tbody > tr > td:contains(中标金额) ::text,"
                                "table > tbody > tr > td:contains(总价) ::text,"
                                "table > tbody > tr > th:contains(中标金额) ::text,"
                                "table > tbody > tr > th:contains(总价) ::text,"
                                "table > tbody > tr > td:contains(价格) ::text,"
                                "table > tbody > tr > th:contains(价格) ::text,"
                                "table > tbody > tr > td:contains(中标价) ::text,"
                                "table > tbody > tr > th:contains(中标价) ::text")
        tmp_alll = response.css("table > tbody > tr:nth-child(1) ::text,"
                               "table > thead > tr:nth-child(1) ::text")
        a = response.css("p:contains(中标金额：) ::text,"
                         "p:contains(中标价):contains(：) ::text")
        if tmp_jin:
            if tmp_alll:
                jine = tmp_jin.extract_first()
                alll = tmp_alll.extract()
                if jine in alll:
                    index = alll.index(jine) + 1
                    winbidder_money = response.css(
                        "table > tbody > tr:nth-child(1)+tr > td:nth-child(" + str(index) + ") ::text,"
                         "table > thead + tbody > tr:nth-child(1) > td:nth-child(" + str(index) + ") ::text")

                    tendering['winbidder_money'] = ''.join(winbidder_money.extract())+"%%%"+''.join(tmp_alll.extract()) if winbidder_money else ''.join(a.extract())
                else :
                    tendering['winbidder_money'] = ''.join(a.extract())
            else:
                tendering['winbidder_money'] = ''.join(a.extract())
        else:
            tendering['winbidder_money'] = ''.join(a.extract())
        begin_time = response.css('p:contains("采购公告"):contains("日期") ::text')
        tendering['begin_time'] = ''.join(begin_time.extract()) if begin_time else ""
        bid_time = response.css('p:contains(定标) ::text')
        tendering['bid_time'] = ''.join(bid_time.extract()) if bid_time else ""
        bid_month = response.css('p:contains(定标) ::text')
        tendering['bid_month'] = ''.join(bid_month.extract()) if bid_month else ""
        tendering['inter_name'] = "浙江政府采购网"
        tendering['website'] = response.url


        jsonstr = (''.join(response.xpath('//*/text()').extract())).replace('\xa0', '')
        jsonstr2 = re.sub("[^({|:|,)]\"[^(}|,|:)]", "", jsonstr)
        str2 = (json.loads(jsonstr2)).get("noticeContent")
        if "}" in str2:
            aa = str2.split("}")[1]
            if aa:
                if "附件信息" in aa:
                    tendering['winbidder_detail'] = aa.split("附件信息")[0]
                else:
                    tendering['winbidder_detail'] = aa
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
        # winbidder_detail = response.xpath('//*/text()')
        # tendering['winbidder_detail'] = str(winbidder_detail.extract()).replace("</p>","\n") if winbidder_detail else ""




        yield tendering
