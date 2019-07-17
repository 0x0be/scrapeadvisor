import logging
import os
import re
import textwrap

from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# parse the output file made by R to retrieve information
class OutputParser:
    def __init__(self):
        self.diz = {}
        self.stats = ""
        self.pos_rev = ""
        self.neg_rev = ""
        self.lang = ""
        self.locations = ""

    def get_lang(self):
        return self.lang

    # parse the .txt file
    def parse(self):
        filepath = "Routput/out.txt"
        if os.path.isfile(filepath):
            try:
                with open(filepath) as f:
                    line = f.readline()
                    cnt = 1
                    while line:
                        if (cnt == 1):
                            if "it" in line:
                                self.lang = "it"
                            else:
                                self.lang = "en"

                        if cnt == 2:
                            line = line.split()[1]
                            line = line.replace(" ", "")
                            self.diz["num_rev"] = line

                        if cnt == 3:
                            line = line.replace("[1]", "")
                            line = line.replace("\"", "")
                            line = line.replace(" ", "")
                            self.diz["from_date"] = line

                        if cnt == 4:
                            line = line.replace("[1]", "")
                            line = line.replace("\"", "")
                            line = line.replace(" ", "")
                            self.diz["to_date"] = line

                        if "bigram" in line:
                            lines = ""
                            for x in range(0, 11):
                                line = f.readline().rstrip()
                                if "<chr>" in line:
                                    lines = "\n"
                                    cnt += 1
                                elif x == 10:
                                    lines += line[0:2] + "). " + line[3:-1].capitalize() + "(" + line[
                                        -1] + ")" + "\n"
                                    cnt += 1
                                else:
                                    lines += "  " + line[1] + "). " + line[3:-1].capitalize() + "(" + line[
                                        -1] + ")" + "\n"
                                    cnt += 1
                            lines = lines.replace(" ", "", 1)  # removes only the first white space which occurs
                            lines = re.sub(' +', ' ', lines)
                            self.diz["bigram"] = lines

                        if "trigram" in line:
                            lines = ""
                            for x in range(0, 11):
                                line = f.readline().rstrip()
                                if "<chr>" in line:
                                    lines = "\n"
                                    cnt += 1
                                elif x == 10:
                                    lines += line[0:2] + "). " + line[3:-1].capitalize() + "(" + line[
                                        -1] + ")" + "\n"
                                    cnt += 1
                                else:
                                    lines += "  " + line[1] + "). " + line[3:-1].capitalize() + "(" + line[
                                        -1] + ")" + "\n"
                                    cnt += 1
                            lines = lines.replace(" ", "", 1)  # removes only the first white space which occurs
                            lines = re.sub(' +', ' ', lines)
                            self.diz["trigram"] = lines

                        if "pos_rev" in line:
                            for x in range(0, 1):
                                line = f.readline().rstrip()
                                line = line.replace("[1]", "")
                                line = line.replace(" ", "", 1)
                                self.diz["pos_rev"] = line

                        if "neg_rev" in line:
                            for x in range(0, 1):
                                line = f.readline().rstrip()
                                line = line.replace("[1]", "")
                                line = line.replace(" ", "", 1)
                                self.diz["neg_rev"] = line

                        if "cities" in line:
                            lines = ""
                            cnt += 1
                            line = f.readline().rstrip()
                            if "tibble" in line:
                                i = int(line.split()[3])
                                i += 3
                                for x in range(0, i):
                                    line = f.readline().rstrip()
                                    if "<chr>" in line:
                                        lines = "\n"
                                        cnt += 1

                                    elif "city" in line:
                                        lines = "\n"
                                        cnt += 1

                                    elif "Groups" in line:
                                        lines = "\n"
                                        cnt += 1

                                    elif "<NA>" in line:
                                        line = line.replace("<", "")
                                        line = line.replace(">", "")
                                        splitted = line.split()
                                        lines += 2 * " " + splitted[0] + "). " + str(
                                            " ".join(splitted[1:-1])) + " (" + str(splitted[-1]) + ")" "\n"
                                        cnt += 1

                                    elif x > 11:  # if number became 10, add only one space
                                        splitted = line.split()
                                        lines += " " + splitted[0] + "). " + str(
                                            " ".join(splitted[1:-1])).capitalize() + " (" + str(splitted[-1]) + ")" "\n"
                                        cnt += 1

                                    else:
                                        splitted = line.split()
                                        lines += 2 * " " + splitted[0] + "). " + str(
                                            " ".join(splitted[1:-1])).capitalize() + " (" + str(splitted[-1]) + ")" "\n"
                                        cnt += 1

                                # lines = lines.replace(" ", "", 1)  # removes only the first white space which occurs
                                # lines = re.sub(' +', ' ', lines)
                                self.diz["cities"] = lines

                        if "states" in line:
                            lines = ""
                            cnt += 1
                            line = f.readline().rstrip()
                            if "tibble" in line:
                                i = int(line.split()[3])
                                i += 2
                                for x in range(0, i):
                                    line = f.readline().rstrip()
                                    if "<chr>" in line:
                                        lines = "\n"
                                        cnt += 1

                                    elif "state" in line:
                                        lines = "\n"
                                        cnt += 1

                                    elif "<NA>" in line:
                                        line = line.replace("<", "")
                                        line = line.replace(">", "")
                                        splitted = line.split()
                                        lines += 2 * " " + splitted[0] + "). " + str(
                                            " ".join(splitted[1:-1])) + " (" + str(
                                            splitted[-1]) + ")" "\n"
                                        cnt += 1

                                    elif x > 11:  # if number became 10, add only one space
                                        splitted = line.split()
                                        lines += " " + splitted[0] + "). " + str(
                                            " ".join(splitted[1:-1])).capitalize() + " (" + str(splitted[-1]) + ")" "\n"
                                        cnt += 1

                                    else:
                                        splitted = line.split()
                                        lines += 2 * " " + splitted[0] + "). " + str(
                                            " ".join(splitted[1:-1])).capitalize() + " (" + str(splitted[-1]) + ")" "\n"
                                        cnt += 1

                                # lines = lines.replace(" ", "", 1)  # removes only the first white space which occurs
                                # lines = re.sub(' +', ' ', lines)
                                self.diz["states"] = lines

                        line = f.readline().rstrip()
                        cnt += 1
                f.close()

            except Exception as e:
                logger.error(e)

        else:
            logger.error("[X]" + filepath + " doesn't exist")

    # save the text
    def save(self):
        for x, y in self.diz.items():
            if x == "pos_rev":
                if self.lang == "en":
                    self.pos_rev += ("Most positive review:\n" + "\n".join(textwrap.wrap(y, width=115)) + "\n\n")
                else:
                    self.pos_rev += ("Recensione più positiva:\n" + "\n".join(textwrap.wrap(y, width=115)) + "\n\n")

            elif x == "neg_rev":
                if self.lang == "en":
                    self.neg_rev += ("Most negative review:\n" + "\n".join(textwrap.wrap(y, width=115)) + "\n\n")
                else:
                    self.neg_rev += ("Recensione più negativa:\n" + "\n".join(textwrap.wrap(y, width=115)) + "\n\n")

            elif x == "cities":
                if self.lang == "en":
                    self.locations += ("Top 10 users' cities:" + y + "\n\n")
                else:
                    self.locations += ("Le top 10 città di provenienza degli utenti:" + y + "\n\n")

            elif x == "states":
                if self.lang == "en":
                    self.locations += ("Top 10 users' states:" + y + "\n\n")
                else:
                    self.locations += ("I top 10 Stati di provenienza gli utenti:" + y + "\n\n")

            else:
                if x == "num_rev":
                    if self.lang == "en":
                        self.stats += ("Number of reviews: " + y + "\n\n")
                    else:
                        self.stats += ("Numero di recensioni: " + y + "\n\n")

                elif x == "from_date":
                    if self.lang == "en":
                        self.stats += ("From: " + y + "\n\n")
                    else:
                        self.stats += ("Da: " + y + "\n\n")

                elif x == "to_date":
                    if self.lang == "en":
                        self.stats += ("To: " + y + "\n\n")
                    else:
                        self.stats += ("A: " + y + "\n\n")

                elif x == "bigram":
                    if self.lang == "en":
                        self.stats += ("Most common pair of consecutive words and number of occurrences: " + y + "\n\n")
                    else:
                        self.stats += (
                                "Le coppie più popolari di parole consecutive e numero di occorrenze:" + y + "\n\n")

                elif x == "trigram":
                    if self.lang == "en":
                        self.stats += ("Most common trio of consecutive words and number of occurrences: " + y + "\n\n")
                    else:
                        self.stats += ("I trii più popolari di parole consecutive e numero di occorrenze:" + y + "\n\n")

    # put text into image
    def to_image(self):
        img1 = Image.new('RGB', (1920, 1080), color=(73, 109, 137))
        img2 = Image.new('RGB', (1920, 1080), color=(73, 109, 137))
        img3 = Image.new('RGB', (1920, 1080), color=(73, 109, 137))
        img4 = Image.new('RGB', (1920, 1080), color=(73, 109, 137))

        font = ImageFont.truetype("C:\Windows\Fonts\Verdana.ttf", 30)

        d1 = ImageDraw.Draw(img1)
        d1.text((50, 10), self.stats, fill=(255, 255, 0), font=font)
        img1.save('Routput/stats.png')

        d2 = ImageDraw.Draw(img2)
        d2.text((50, 50), self.pos_rev, fill=(255, 255, 0), font=font)
        img2.save('Routput/pos_rev.png')

        d3 = ImageDraw.Draw(img3)
        d3.text((50, 50), self.neg_rev, fill=(255, 255, 0), font=font)
        img3.save('Routput/neg_rev.png')

        d4 = ImageDraw.Draw(img4)
        d4.text((50, 50), self.locations, fill=(255, 255, 0), font=font)
        img4.save('Routput/locations.png')

# Example
# o = OutputParser()
# o.parse()
# o.save()
# o.to_image()
