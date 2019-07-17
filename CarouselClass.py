import os
import time
import logging

from pathlib import Path
from kivy.app import App
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
from OutputParser import OutputParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Carousel for sliding graphs
class CarouselApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lang = ""

    def set_lang(self, arg):
        self.lang = arg

    def build(self):
        # create the Routput directory if not exists
        try:
            os.mkdir("Routput")
        except OSError:
            logger.info("Routput directory already exists")
        else:
            logger.info("Successfully created the directory Routput")

        # create OutputParser object to parse analysis output
        output_parser = OutputParser()
        output_parser.parse()
        output_parser.save()
        output_parser.to_image()
        time.sleep(1)

        # create Carousel object
        carousel = Carousel(direction='right')

        # and add images from Routput
        try:
            if Path("Routput/stats.png").is_file():
                image1 = AsyncImage(source="Routput/stats.png", nocache=True)
                carousel.add_widget(image1)

            if Path("Routput/locations.png").is_file():
                image2 = AsyncImage(source="Routput/locations.png", nocache=True)
                carousel.add_widget(image2)

            if Path("Routput/neg_rev.png").is_file():
                image3 = AsyncImage(source="Routput/neg_rev.png", nocache=True)
                carousel.add_widget(image3)

            if Path("Routput/pos_rev.png").is_file():
                image4 = AsyncImage(source="Routput/pos_rev.png", nocache=True)
                carousel.add_widget(image4)

            # if Path("Routput/world_map.png").is_file() and os.path.getsize("Routput/world_map.png") > 3000:
            #   image5 = AsyncImage(source="Routput/world_map.png", nocache=True)
            #    carousel.add_widget(image5)

            if Path("Routput/rev_per_week.png").is_file():
                image6 = AsyncImage(source="Routput/rev_per_week.png", nocache=True)
                carousel.add_widget(image6)

            if Path("Routput/25_most_common_words.png").is_file():
                image7 = AsyncImage(source="Routput/25_most_common_words.png", nocache=True)
                carousel.add_widget(image7)

            if Path("Routput/25_wordclouds.png").is_file():
                image8 = AsyncImage(source="Routput/25_wordclouds.png", nocache=True)
                carousel.add_widget(image8)

            if Path("Routput/9_growing.png").is_file():
                image9 = AsyncImage(source="Routput/9_growing.png", nocache=True)
                carousel.add_widget(image9)

            if Path("Routput/9_decreasing.png").is_file():
                image10 = AsyncImage(source="Routput/9_decreasing.png", nocache=True)
                carousel.add_widget(image10)

            if Path("Routput/sent_afinn.png").is_file():
                image11 = AsyncImage(source="Routput/sent_afinn.png", nocache=True)
                carousel.add_widget(image11)

            # check if reviews are in Italian or English
            if output_parser.get_lang() == "en":
                logger.info("[*] Reviews are in English")
                if Path("Routput/sent_bing.png").is_file():
                    image12 = AsyncImage(source="Routput/sent_bing.png", nocache=True)
                    carousel.add_widget(image12)
            else:
                logger.info("[*] Reviews are in Italian")
                if Path("Routput/25_not_follows.png").is_file():
                    image12 = AsyncImage(source="Routput/25_not_follows.png", nocache=True)
                    carousel.add_widget(image12)

            if Path("Routput/not_follows.png").is_file():
                image13 = AsyncImage(source="Routput/not_follows.png", nocache=True)
                carousel.add_widget(image13)

        except Exception as e:
            logger.error(e)

        return carousel
