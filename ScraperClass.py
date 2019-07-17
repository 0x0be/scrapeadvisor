import io
import webbrowser
import requests
import unicodecsv as csv
import logging
from bs4 import BeautifulSoup

DB_COLUMN = 'review_title'
DB_COLUMN1 = 'review_body'
DB_COLUMN2 = 'review_date'
DB_COLUMN3 = 'contributions'
DB_COLUMN4 = 'helpful_vote'
DB_COLUMN5 = 'user_location'
DB_COLUMN6 = 'rating'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScraperClass:
    def __init__(self, url):
        self.headers = [
            DB_COLUMN,
            DB_COLUMN1,
            DB_COLUMN2,
            DB_COLUMN3,
            DB_COLUMN4,
            DB_COLUMN5,
            DB_COLUMN6,
        ]
        self.start_url = [url]
        self.lang = 'it'
        # self.get_review()
        self.item_list = list()
        self.dict = dict()
        self.filename = ""

    def get_review(self):
        for url in self.start_url:
            items = self.scrape(url, self.lang)
            if not items:
                logger.info('No reviews')
            else:
                # write in CSV
                filename = url.split('Reviews-')[1][:-5] + '__' + self.lang
                logger.info('filename:', filename)
                self.filename = filename
                self.write_in_csv(items, filename + '.csv', self.headers, mode='wb')

    def scrape(self, url, lang):
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0',
        })
        items = self.parse(session, url + '?filterLang=' + lang)
        return items

    def parse(self, session, url):
        # get number of reviews and start getting sub-pages with reviews
        logger.info('[parse] url:', url)
        soup = self.get_soup(session, url)
        if not soup:
            logger.error('[parse] no soup:', url)
            return
        num_reviews = soup.find('span', class_='reviews_header_count').text  # get text
        num_reviews = num_reviews[1:-1]
        num_reviews = num_reviews.replace(',', '')
        num_reviews = int(num_reviews)  # convert text into integer
        logger.info('[parse] num_reviews ALL:', num_reviews)
        url_template = url.replace('.html', '-or{}.html')
        logger.info('[parse] url_template:', url_template)
        items = []
        offset = 0

        while True:
            subpage_url = url_template.format(offset)
            subpage_items = self.parse_reviews(session, subpage_url)
            if not subpage_items:
                break
            items += subpage_items
            if len(subpage_items) < 10:
                break
            offset += 10
        return items

    def get_soup(self, session, url, show=False):
        r = session.get(url)
        if show:
            self.display(r.content, 'temp.html')
        if r.status_code != 200:  # not OK
            logger.info('[get_soup] status code:', r.status_code)
        else:
            return BeautifulSoup(r.text, 'html.parser')

    def post_soup(self, session, url, params, show=False):
        # read HTML from server and convert to Soup
        r = session.post(url, data=params)
        if show:
            self.display(r.content, 'temp.html')
        if r.status_code != 200:  # not OK
            logger.error('[post_soup] status code:', r.status_code)
        else:
            return BeautifulSoup(r.text, 'html.parser')

    def display(self, content, filename='output.html'):
        with open(filename, 'wb') as f:
            f.write(content)
            webbrowser.open(filename)

    def parse_reviews(self, session, url):
        # get all reviews from one page
        logger.info('[parse_reviews] url:', url)
        soup = self.get_soup(session, url)

        if not soup:
            logger.error('[parse_reviews] no soup:', url)
            return

        facility_name = soup.find('h1', class_='header heading masthead masthead_h1').text
        reviews_ids = self.get_reviews_ids(soup)
        if not reviews_ids:
            return

        soup = self.get_more(session, reviews_ids)
        if not soup:
            logger.error('[parse_reviews] no soup:', url)
            return

        items = []
        for idx, review in enumerate(soup.find_all('div', class_='reviewSelector')):
            badgets = review.find_all('span', class_='badgetext')

            if len(badgets) > 0:
                contributions = badgets[0].text
            else:
                contributions = '0'

            if len(badgets) > 1:
                helpful_vote = badgets[1].text
            else:
                helpful_vote = '0'
            user_loc = review.select_one('div.userLoc strong')

            if user_loc:
                splitted = user_loc.text.split(",")  # we want to delete regions like "Pavia, Lombardia, Italia"
                if len(splitted) > 2:
                    user_loc = splitted[0] + "," + splitted[2]  # taking only city and state
                else:
                    user_loc = user_loc.text
            else:
                user_loc = 'NA'
            bubble_rating = review.select_one('span.ui_bubble_rating')['class']
            bubble_rating = bubble_rating[1].split('_')[-1][-2]
            item = {
                'review_title': review.find('span', class_='noQuotes').text,
                'review_body': review.find('p', class_='partial_entry').text,
                'review_date': review.find('span', class_='ratingDate')['title'],
                'contributions': contributions,
                'helpful_vote': helpful_vote,
                'user_location': user_loc,
                'rating': bubble_rating
            }

            items.append(item)
            logger.info('\n--- review ---\n')
            dict_item = dict()
            for key, val in item.items():
                logger.info(' ', key, ':', val)
                dict_item[key] = val
            self.item_list.append([dict_item])
        return items

    def get_filename(self):
        return self.filename

    def get_reviews_ids(self, soup):
        items = soup.find_all('div', attrs={'data-reviewid': True})
        if items:
            reviews_ids = [x.attrs['data-reviewid'] for x in items][::2]
            logger.info('[get_reviews_ids] data-reviewid:', reviews_ids)
            return reviews_ids

    def get_more(self, session, reviews_ids):
        url = 'https://www.tripadvisor.com/OverlayWidgetAjax?Mode=EXPANDED_HOTEL_REVIEWS_RESP&metaReferer=Hotel_Review'
        payload = {
            'reviews': ','.join(reviews_ids),  # ie. "577882734,577547902,577300887",
            'widgetChoice': 'EXPANDED_HOTEL_REVIEW_HSX',
            'haveJses': 'earlyRequireDefine,amdearly,global_error,long_lived_global,apg-Hotel_Review,'
                        'apg-Hotel_Review-in,bootstrap,desktop-rooms-guests-dust-en_US,'
                        'responsive-calendar-templates-dust-en_US,taevents',
            'haveCsses': 'apg-Hotel_Review-in',
            'Action': 'install',
        }
        soup = self.post_soup(session, url, payload)
        return soup

    def write_in_csv(self, items, filename='results.csv',
                     headers=None,
                     mode='w'):
        if headers is None:
            headers = ['hotel name', 'review title', 'review body',
                       'review date', 'contributions', 'helpful vote',
                       'user name', 'user location', 'rating']
        logger.info('--- CSV ---')
        with io.open(filename, mode) as csvfile:
            csv_file = csv.DictWriter(csvfile, headers, encoding='utf-8')
            if mode == 'wb':
                csv_file.writeheader()
            csv_file.writerows(items)

    def get_item(self):
        return self.item_list

# TrpAdvScrp = ScraperClass('http://www.tripadvisor..')
# TrpAdvScrp.get_review()
