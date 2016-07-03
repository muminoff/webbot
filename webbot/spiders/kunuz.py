# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractor import LinkExtractor
from webbot.items import PageItem
from bs4 import BeautifulSoup


class KunuzSpider(scrapy.Spider):
    name = "kunuz"
    link_extractor = LinkExtractor()
    allowed_domains = ["kun.uz"]
    start_urls = (
        'http://www.kun.uz/',
    )
    visited_urls = set()

    def parse(self, response):
        hxs = scrapy.Selector(response)
        extracted_links = self.link_extractor.extract_links(response)

        page_urls = [link.url for link in extracted_links]

        self.logger.info('Crawling URL -> {}'.format(response.url))

        item = PageItem()
        item['url'] = response.url
        item['title'] = hxs.xpath('/html/head/title/text()').extract()[0].strip()
        soup = BeautifulSoup(response.body)
        for tag in soup(["title", "script", "style"]):
            tag.extract()

        clean_text = u' '.join(a for a in soup.get_text().split())
        item['content'] = clean_text

        self.visited_urls.add(response.url)

        yield item

        for link in page_urls:
            self.logger.info('Following link {}'.format(link))
            if link not in self.visited_urls:
                yield scrapy.http.Request(url=link, callback=self.parse)
            else:
                self.logger.warning('Already visited {}'.format(link))
