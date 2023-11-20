import scrapy

import config

from datetime import datetime, date
from typing import Optional, Generator

from scrapy import Request, Selector
from scrapy.http import Response


class VacanciesSpider(scrapy.Spider):
    name = "vacancies"
    allowed_domains = ["djinni.co"]
    start_urls = ["https://djinni.co/jobs/?primary_keyword=Python"]

    def parse(
        self, response: Response, **kwargs: Optional[dict]
    ) -> Generator[scrapy.Request, None, None]:
        vacancy_links = response.css(
            ".job-list-item__link::attr(href)"
        ).extract()
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

        company = self.get_company(response)
        salary = self.get_salary(response)
        english_level = self.get_english_level(sel)
        experience_year = self.get_experience_year(response)
        domen = self.get_domen(sel)
        work_type, company_type, test_available = self.get_additional_info(sel)
        views = self.get_views(response)
        applications = self.get_applications(response)
        publication_date = self.get_publication_date(response)
        technologies = self.get_technologies(response)
        yield {
            "title": response.css("h1::text").get().strip(),
            "company": company,
            "salary": salary,
            "english_level": english_level,
            "experience_year": experience_year,
            "domen": domen,
            "work_type": work_type,
            "company_type": company_type,
            "test_available": test_available,
            "views": views,
            "applications": applications,
            "publication_date": publication_date,
            "technologies": technologies,
        }

    @staticmethod
    def get_technologies(response: Response) -> list:
        description = " ".join(response.css("div.mb-4::text").getall()).strip()
        technologies_list = config.technologies
        current_technologies_list = []
        for technology in technologies_list:
            if technology.lower() in description.lower():
                current_technologies_list.append(technology)
        return current_technologies_list

    @staticmethod
    def get_company(response: Response) -> Optional[str]:
        return (
            response.css(".job-details--title::text").get().strip()
            if response.css(".job-details--title::text")
            else None
        )

    @staticmethod
    def get_salary(response: Response) -> Optional[str]:
        return (
            response.css(".public-salary-item::text").get().strip()
            if response.css(".public-salary-item::text")
            else None
        )

    @staticmethod
    def get_english_level(sel: Selector) -> Optional[str]:
        english_level = sel.xpath(
            '//div[contains(text(), "Англійська:")]/text()'
        ).get()
        return english_level.strip().split(": ")[1] if english_level else None

    @staticmethod
    def get_experience_year(response: Response) -> Optional[int]:
        exp_text = response.css(
            ".job-additional-info--body li:last-child div::text"
        ).get()
        if exp_text:
            experience_year = int(exp_text.split()[0].replace("Без", "0"))
            return experience_year
        return None

    @staticmethod
    def get_domen(sel: Selector) -> Optional[str]:
        domen = sel.xpath('//div[contains(text(), "Домен:")]/text()').get()
        return domen.strip().split(": ")[1] if domen else None

    @staticmethod
    def get_additional_info(sel: Selector) -> tuple:
        work_type, company_type, test_available = None, None, None
        items = sel.css("li.job-additional-info--item")
        for item in items:
            icon_class = item.css("span::attr(class)").get()
            text = item.css("div.job-additional-info--item-text::text").get()

            if "bi bi-building" in icon_class:
                work_type = text.strip() if text else None
            elif "bi bi-basket3-fill" in icon_class:
                company_type = text.strip() if text else None
            elif "bi bi-exclude" in icon_class:
                company_type = text.strip() if text else None
            elif (
                "bi bi-pencil-square" in icon_class
                and text == "Є тестове завдання"
            ):
                test_available = 1

        return work_type, company_type, test_available

    @staticmethod
    def get_views(response: Response) -> int:
        views_text = response.css("p.text-muted").re_first(r"(\d+) відгук")
        return int(views_text) if views_text else 0

    @staticmethod
    def get_applications(response: Response) -> int:
        apps_text = response.css("p.text-muted").re_first(r"(\d+) відгук")
        return int(apps_text) if apps_text else 0

    def get_publication_date(self, response: Response) -> date:
        date_text = response.css("p.text-muted").extract_first()
        publication_date = (
            date_text.split("Вакансія опублікована")[-1]
            .strip()
            .split("<br>")[0]
            .strip()
        )
        return self.format_data(publication_date)

    @staticmethod
    def format_data(publication_date: str) -> date:
        months_dict = {
            "січня": "January",
            "лютого": "February",
            "березня": "March",
            "квітня": "April",
            "травня": "May",
            "червня": "June",
            "липня": "July",
            "серпня": "August",
            "вересня": "September",
            "жовтня": "October",
            "листопада": "November",
            "грудня": "December",
        }
        for k, v in months_dict.items():
            publication_date = publication_date.replace(k, v)

        date_obj = datetime.strptime(publication_date, "%d %B %Y")
        date_only = date_obj.date()
        return date_only
