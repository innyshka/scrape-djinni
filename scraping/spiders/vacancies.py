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

        company = response.css(".job-details--title::text").get()
        salary = response.css(".public-salary-item::text").get()
        english_level = sel.xpath('//div[contains(text(), "Англійська:")]/text()').get()
        experience_year = int(
            response.css(
                ".job-additional-info--body li:last-child div::text"
            )
            .get()
            .split()[0]
            .replace("Без", "0")
        )
        domen = sel.xpath('//div[contains(text(), "Домен:")]/text()').get()

        work_type = None
        company_type = None
        test_available = None

        items = sel.css('li.job-additional-info--item')
        for item in items:
            icon_class = item.css('span::attr(class)').get()
            text = item.css('div.job-additional-info--item-text::text').get()

            if 'bi bi-building' in icon_class:
                work_type = text.strip() if text else None
            elif 'bi bi-basket3-fill' in icon_class:
                company_type = text.strip() if text else None
            elif 'bi bi-exclude' in icon_class:
                company_type = text.strip() if text else None
            elif 'bi bi-pencil-square' in icon_class and text == 'Є тестове завдання':
                test_available = 1

        yield {
            "title": response.css("h1::text").get().strip(),
            "company": company.strip() if company else None,
            "salary": salary.strip() if salary else None,
            "english_level": english_level.strip().split(": ")[1] if english_level else None,
            "experience_year": experience_year if experience_year else None,
            "domen": domen.strip().split(": ")[1] if domen else None,
            "work_type": work_type,
            "company_type": company_type,
            "test_available": test_available,
        }
