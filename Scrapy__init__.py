# coding=utf-8
# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import scrapy
import logging
from scrapy.http import FormRequest
import datetime
from ptt.items import PostItem
import re





class PTTSpider(scrapy.Spider):
    name = 'ptt'
    allowed_domains = ['ptt.cc']
    start_urls = ('https://www.ptt.cc/bbs/Gossiping/index.html', )
    _retries = 0
    MAX_RETRY = 1
    _pages = 0
    MAX_PAGES = 4  #Maxixum number of crawled pages
    total_score_threshold = 20 # Threshold of push score (for filtering)
    keyword = [u'政治',u'藍營',u'綠營',u'總統','立法',u'行政',u'執政',] # Please specify your keyword
    keyword_count_threshold = 1 # Threshold of keyword occurence (for filtering)
    

  
    def parse(self, response):
         if len(response.xpath('//div[@class="over18-notice"]')) > 0:
            if self._retries < PTTSpider.MAX_RETRY:
                self._retries += 1
                logging.warning('retry {} times...'.format(self._retries))
                yield FormRequest.from_response(response,
                                                formdata={'yes': 'yes'},
                                                callback=self.parse)
            else:
                logging.warning('!!!!!!!!!!!!!!!!!you cannot pass!!!!!!!!!!!!!!')
         else:
                filename = response.url.split('/')[-2] + '.html' 
                

                with open(filename, 'wb') as f:
                    f.write(response.body)
                    self._pages += 1

                for href in response.css('.r-ent > div.title > a::attr(href)'):
                    url = response.urljoin(href.extract())
                    yield scrapy.Request(url, callback=self.parse_post)

                if self._pages < PTTSpider.MAX_PAGES:
                    next_page = response.xpath(u'//div[@id="action-bar-container"]//a[contains(text(), "上頁")]/@href')
                    logging.warning(next_page)
                    logging.warning('231')
                    if next_page:
                        url = response.urljoin(next_page[0].extract())
                        yield scrapy.Request(url, self.parse)
                    else:
                        logging.warning('no next page')
                else:
                    logging.warning('max pages reached')
                    
    def parse_post(self, response):
     
        item = PostItem()      
#        item['title'] =  response.xpath(
#            '//meta[@property="og:title"]/@content')[0].extract() 
#        item['author'] = response.xpath(
#            u'//div[@class="article-metaline"]/span[text()="作者"]/following-sibling::span[1]/text()')[
#                0].extract().split(' ')[0]
#        datetime_str = response.xpath(
#            u'//div[@class="article-metaline"]/span[text()="時間"]/following-sibling::span[1]/text()')[
#                0].extract()
#        item['date'] = datetime.datetime.strptime(datetime_str, '%a %b %d %H:%M:%S %Y')

#        item['content'] = response.xpath('//div[@id="main-content"]/text()')[0].extract()

        comments = []
        total_score = 0
        for comment in response.xpath('//div[@class="push"]'):
            push_tag = comment.css('span.push-tag::text')[0].extract()
            push_user = comment.css('span.push-userid::text')[0].extract()
            push_content = comment.css('span.push-content::text')[0].extract()

            if u'推' in push_tag:
                score = 1
            elif u'噓' in push_tag:
                score = -1
            else:
                score = 0

            total_score += score

            comments.append({'user': push_user,
                             'content': push_content,
                             'score': score})

 #      item['comments'] = comments
 #       item['score'] = total_score
 #       item['url'] = response.url
        
        if total_score >=  self.total_score_threshold:
            check_content = response.xpath('//div[@id="main-content"]/text()')[
            0].extract()
            
            keyword_count = 0   
            for i in range(0,len(self.keyword),1):
                if re.search(self.keyword[i],check_content):
                   keyword_count+=1
                else:
                   continue
            if keyword_count >= self.keyword_count_threshold:
                incontent = response.xpath('//div[@id="main-content"]')
                for incontent_href in incontent.css('a::attr(href)'):
                  if re.search('.png',incontent_href.extract()):  
                      item['incontent_url'] = incontent_href.extract()
                      item['incontent_url_type'] = '.png'
                      
                  if re.search('.jpg',incontent_href.extract()):
                       item['incontent_url'] = incontent_href.extract()
                       item['incontent_url_type'] = '.jpg'

        yield item
