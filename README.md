# 📊 Djinni vacancies analysis for Python Developers
A web scraping and data analysis project that provides Djinni vacancies statistics for Python developers.

## 👩‍💻 Technologies
* Scrapy
* Pandas
* NumPy
* Matplotlib

## ⚙️ Installations

✅ Python 3 must be installed

```shell
git clone https://github.com/innyshka/scrape-djinni.git
cd scrape-djinni
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

## 🕵️‍♀️ Run scrapy crawl 
```shell
scrapy crawl vacancies -O vacancies.csv
```

📍 In `vacancies.csv` you can see all information about vacancies:
* `title`
* `company`
* `salary`
* `english_level`
* `experience_year`
* `domen`
* `work_type`
* `company_type`
* `test_available`
* `views`
* `applications`
* `publication_date`
* `technologies` (you can change technology-keyword in [config file](config.py))

## 👩‍🔬 Run Analytics
Open [analytics file](analytics/vacansies_analytics.ipynb) and run all cells in order (`Ctrl+Alt+Shift+Enter`)

📍 You can also look in [the diagrams folder](analytics/diagrams), which is relevant as of November 20, 2023

### 📎 Example
![Top 30 Most Mentioned Technologies](analytics/diagrams/Top%2030%20Most%20Mentioned%20Technologies.png)
