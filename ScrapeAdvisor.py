import glob
import os
import subprocess
import threading
import time
import kivy
import logging

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from CarouselClass import CarouselApp
from ScraperClass import ScraperClass

kivy.require("1.9.0")

kv = """    
<Row@BoxLayout>:
    canvas.before:
        Color:
            rgba: 0.5, 0.5, 0.5, 1
        Rectangle:
            size: self.size
            pos: self.pos
    value: ''
    ScrollView:
        size: self.size
        Label:
            padding_x: dp(10)
            padding_y: dp(10)
            text: root.value
            #halign: 'left'
            #valign: 'top'
            size_hint_y: None
            text_size: self.width, None
            height: self.texture_size[1]
            markup: True
<Test>:
    canvas:
        Color:
            rgba: 0.3, 0.3, 0.3, 1
        Rectangle:
            size: self.size
            pos: self.pos
    rv: rv
    orientation: 'vertical'
    GridLayout:
        cols: 2
        rows: 1
        size_hint_y: None
        height: dp(50)
        padding: dp(8)
        spacing: dp(16)
        TextInput:
            id: input_url
            multiline: False
            size_hint_x: 6
            hint_text: 'http://www.tripadvisor.com/'
            padding: dp(10), dp(10), 0, 0
            on_text_validate: root.thread_rev(input_url.text)
        Button:
            text: 'Enter'
            on_press: root.thread_rev(input_url.text)
    GridLayout:
        cols: 3
        rows: 1
        size_hint_y: None
        height: dp(70)
        padding: dp(8)
        spacing: dp(16)
        rv: rv.__self__
        Button:
            text: 'Show Reviews'
            on_press: root.show_review()
        Button:
            text: 'Sentiment Analysis'
            on_press: root.thread_sent()
        Button:
            text: 'About'
            on_press: root.about()
    RecycleView:
        id: rv
        scroll_type: ['bars', 'content']
        scroll_wheel_distance: dp(114)
        bar_width: dp(20)
        viewclass: 'Row'
        RecycleBoxLayout:
            padding: dp(30)
            default_size: None, dp(200)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
            spacing: dp(10)
"""

Builder.load_string(kv)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Test(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = Label(markup=True)
        self.img = Image(source='res/about.png')
        self.carousel = CarouselApp().build()
        self.add_widget(self.label)
        self.is_info_visible = True
        self.is_rv_visible = True
        self.is_img_visible = False
        self.is_car_visible = False
        self.new_url = False
        self.scraper = None
        self.lang = ""

    # thread for downloading the reviews
    def thread_rev(self, input_url):
        # removes older reviews loaded
        if self.rv.data:
            self.rv.data = []

        self.new_url = False

        # check for displayed labels/widget
        if self.is_rv_visible:
            self.remove_widget(self.ids.rv)
            self.is_rv_visible = False

        if self.is_car_visible:
            self.remove_widget(self.carousel)
            self.is_car_visible = False

        if self.is_img_visible:
            self.remove_widget(self.img)
            self.is_img_visible = False

        # remove all csv files
        for f in glob.glob("*.csv"):
            os.remove(f)

        # get language
        self.get_lang(input_url)

        # and the content of prev R plot
        files = glob.glob('Routput/*')
        for f in files:
            os.remove(f)

        if self.is_info_visible:
            self.label.text = '[size=40][b][color=ffffff]Loading reviews[/color][/b][/size]'
        else:
            self.add_widget(self.label)
            self.label.text = '[size=40][b][color=ffffff]Loading reviews[/color][/b][/size]'
            self.is_info_visible = True

        # start thread for downloading reviews
        thread = threading.Thread(target=self.calculate, args=(input_url,))
        logger.info("Input url: " + input_url)
        thread.daemon = True
        thread.start()
        logger.info("[*] Downloading thread started")

    # thread for sentiment analysis
    def thread_sent(self):
        thread = threading.Thread(target=self.sentiment)
        thread.daemon = True
        thread.start()

    # function called when "Equals" is pressed
    def calculate(self, calculation):
        try:
            self.scraper = ScraperClass(calculation)
            self.scraper.get_review()
            self.label.text = '[size=40][b][color=#4caf50]Reviews loaded[/color][/b][/size]'

        except Exception as e:
            logger.error(e)
            logger.error("[X] Invalid URL")
            time.sleep(1)
            self.label.text = '[size=40][b][color=f44336]Invalid URL[/color][/b][/size]'

    # function called when "Show Reviews" is pressed
    def show_review(self):
        try:
            if self.is_info_visible:
                self.remove_widget(self.label)
                self.is_info_visible = False

            if self.is_car_visible:
                self.remove_widget(self.carousel)
                self.is_car_visible = False

            if self.is_img_visible:
                self.remove_widget(self.img)
                self.is_img_visible = False

            if not self.is_rv_visible:
                self.add_widget(self.ids.rv)
                self.is_rv_visible = True

            self.rv.data = [{'value': '[size=17][b]' + "Title: " + '[/b][/size]' + x[0][
                'review_title'].lower().capitalize() + "\n" +
                                      '[size=17][b]' + "Review: " + '[/b][/size]' + x[0][
                                          'review_body'].lower().capitalize() + "\n" +
                                      '[size=17][b]' + "Date: " + '[/b][/size]' + x[0]['review_date'] + "\n" +
                                      '[size=17][b]' + "User Location: " + '[/b][/size]' + x[0][
                                          'user_location'] + "\n" +
                                      '[size=17][b]' + "Rating: " + '[/b][/size]' + x[0]['rating'] + "\n" +
                                      '[size=17][b]' + "Contribution: " + '[/b][/size]' + x[0]['contributions'] + "\n" +
                                      '[size=17][b]' + "Helpful Vote: " + '[/b][/size]' + x[0]['helpful_vote']} for x in
                            self.scraper.get_item()]

            if not self.rv.data:
                self.remove_widget(self.ids.rv)
                self.is_rv_visible = False
                if self.is_info_visible:
                    self.label.text = '[size=40][b][color=f44336]No data to load[/color][/b][/size]'
                else:
                    self.add_widget(self.label)
                    self.label.text = '[size=40][b][color=f44336]No data to load[/color][/b][/size]'
                    self.is_info_visible = True

        except Exception as e:
            logger.error(e)
            self.remove_widget(self.ids.rv)
            self.is_rv_visible = False
            logger.error("[X] No data to load")
            if self.is_info_visible:
                self.label.text = '[size=40][b][color=f44336]No data to load[/color][/b][/size]'
            else:
                self.add_widget(self.label)
                self.label.text = '[size=40][b][color=f44336]No data to load[/color][/b][/size]'
                self.is_info_visible = True

    # function called when "Sentiment Analysis" is pressed
    def sentiment(self):
        try:
            # when the url provided is not changed
            if self.new_url:
                if self.is_rv_visible:
                    self.remove_widget(self.ids.rv)
                    self.is_rv_visible = False

                if self.is_img_visible:
                    self.remove_widget(self.img)
                    self.is_img_visible = False

                if not self.is_car_visible:
                    self.add_widget(self.carousel)
                    self.is_car_visible = True

            # the url is new
            else:
                # removes older reviews loaded
                if self.is_rv_visible:
                    self.remove_widget(self.ids.rv)
                    self.is_rv_visible = False

                if self.is_car_visible:
                    self.remove_widget(self.carousel)
                    self.is_car_visible = False

                if self.is_img_visible:
                    self.remove_widget(self.img)
                    self.is_img_visible = False

                if self.is_info_visible:
                    self.label.text = '[size=40][b][color=ffffff]Running R sentiment analysis[/color][/b][/size]'
                    time.sleep(1)
                else:
                    self.add_widget(self.label)
                    self.label.text = '[size=40][b][color=ffffff]Running R sentiment analysis[/color][/b][/size]'
                    time.sleep(1)
                    self.is_info_visible = True

                # checks if there's a csv file somewhere
                if self.scraper.get_filename():
                    try:
                        subprocess.call(
                            ["C:/Program Files/R/R-3.5.3/bin/x64/Rscript.exe", "Rinput/" + self.lang + ".R",
                             self.scraper.get_filename() + ".csv"],
                            shell=True)
                        self.label.text = '[size=40][b][color=#4caf50]Done[/color][/b][/size]'
                        time.sleep(1)
                        self.remove_widget(self.ids.rv)

                        # create Carousel object and display it
                        if not self.is_car_visible:
                            self.carousel = CarouselApp().build()
                            self.remove_widget(self.label)
                            self.is_info_visible = False
                            self.add_widget(self.carousel)
                            self.is_car_visible = True
                            self.new_url = True

                    except Exception as e:
                        logger.error(e)
                        if self.is_info_visible:
                            self.label.text = '[size=40][b][color=f44336]No CSV file found[/color][/b][/size]'
                        else:
                            self.add_widget(self.label)
                            self.label.text = '[size=40][b][color=f44336]No CSV file found[/color][/b][/size]'
                            self.is_info_visible = True
                        logger.error("[X] No CSV file found")
                else:
                    self.label.text = '[size=40][b][color=f44336]No CSV file found[/color][/b][/size]'
                    logger.error("[X] No CSV file found")

        except Exception as e:
            logger.error(e)
            self.label.text = '[size=40][b][color=f44336]No CSV file found[/color][/b][/size]'
            logger.error("[X] No CSV file found")

    # function called when "About" is pressed
    def about(self):
        # check for displayed labels/widget
        if self.is_rv_visible:
            self.remove_widget(self.ids.rv)
            self.is_rv_visible = False

        if self.is_car_visible:
            self.remove_widget(self.carousel)
            self.is_car_visible = False

        if self.is_info_visible:
            self.remove_widget(self.label)
            self.is_info_visible = False

        if not self.is_img_visible:
            self.add_widget(self.img)
            self.is_img_visible = True

    # get language of reviews
    def get_lang(self, domain):
        if "www.tripadvisor.it" in domain:
            self.lang = "it"

        elif "www.tripadvisor.com" in domain:
            self.lang = "en"

        else:
            logger.error("[X] Language not supported")


# main class
class ScrapeAdvisor(App):
    def build(self):
        return Test()


# run baby run run
if __name__ == '__main__':
    ScrapeAdvisor().run()
