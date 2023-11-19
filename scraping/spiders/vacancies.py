from typing import Optional, Generator

import scrapy
from scrapy import Request, Selector
from scrapy.http import Response


class VacanciesSpider(scrapy.Spider):
    name = "vacancies"
    allowed_domains = ["djinni.co"]
    start_urls = ["https://djinni.co/jobs/?primary_keyword=Python"]

    def parse(self, response: Response, **kwargs: Optional[dict]) -> Generator[scrapy.Request, None, None]:
        vacancy_links = response.css(".job-list-item__link::attr(href)").extract()
        for vacancy_link in vacancy_links:
            yield Request(
                response.urljoin(vacancy_link), callback=self.parse_vacancy
            )

        next_page = response.css(
            ".pagination li:last-child a::attr(href)"
        ).get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_vacancy(self, response: Response) -> Generator[dict, None, None]:
        sel = Selector(text=response.body)
        english_level = sel.xpath('//div[contains(text(), "Англійська:")]/text()').get()
        experience = sel.xpath('//div[contains(text(), "роки досвіду")]/text()').get()

        yield {
            "vacancy": response.css("h1::text").get().strip(),
            "english_level": english_level.strip().split(":")[1] if english_level else None,
            "experience_year": experience.strip().split()[0] if experience else None,
        }
