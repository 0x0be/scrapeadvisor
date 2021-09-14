<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://github.com/blackeko/scrapeadvisor/blob/media/logo.png" alt="Project logo"></a>
</p>

<h3 align="center">scrapeadvisor</h3>

<div align="center">

  [![Status](https://img.shields.io/badge/status-active-success.svg)]() 
  [![License](https://img.shields.io/badge/license-GPL3-blue.svg)](/LICENSE)

</div>

---

<p align="center">
	A user-friendly python-based GUI which provides sentiment analysis of users' reviews toward a specific TripAdvisor facility 
    <br> 
</p>

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Run](#run)
- [Usage](#usage)
- [Statistics](#statistics)
- [Supported Languages](#languages)
- [Built Using](#built_using)
- [Authors](#authors)
- [Acknowledgments](#acknowledgement)
- [Disclaimer](#disclaimer)

## About <a name = "about"></a>

If you're reading, dear Tripadvisor, Inc., hire me!

## Getting Started <a name = "getting_started"></a>

### Prerequisites

- [Python](https://www.python.org/downloads/) installed 
- [R](https://cran.r-project.org/bin/windows/base/) installed 

### Installing

Make sure you've all Python dependencies installed with:

```console
scrape@advisor:~$ pip3 install -r requirements.txt
```

Also, the following R packages are needed:

- dplyr 
- readr 
- lubridate
- ggplot2
- tidytext
- tidyverse 
- stringr
- tidyr
- scales
- broom 
- purrr
- widyr 
- igraph
- ggraph
- SnowballC
- wordcloud
- reshape2
- TeachingDemos

You can manually install missing ones with: 

```R
install.packages("library_name")
```

or run [this script](https://github.com/blackeko/scrapeadvisor/blob/master/ipak.R) (credit to [@stevenworthington](https://gist.github.com/stevenworthington)) to install them all.

### Note

For Italian language support, **TextWiller** library must be installed.<br/>
To do that:

```R
install.packages("devtools") 
install_github("livioivil/TextWiller")
```

## Run <a name = "run"></a>

In order to launch *scrapeadvisor* GUI, run:

```console
scrape@advisor:~$ python3 ScrapeAdvisor.py
```

## Usage <a name="usage"></a>

### Insert URL

1. Insert the main page URL of a TripAdvisor structure (pub/restaurant/hotel/whatever) in the **URL bar** and click **Enter** (or press Enter)
2. Wait until **"Reviews Loaded"** label appears (may take time, depending on number of reviews)

### Show Reviews

After the download is finished, press **"Show Reviews"** to see all the downloaded reviews.

### Sentiment Analysis

After the download is finished, press **"Sentiment Analysis"** button and wait: all the graphs related to the facility will appear follow after, so you can **swipe** between them.

## Statistics <a name="statistics"></a>

- Frequent **couple/trio of consecutive words** (bigrams/trigrams)
- Most **positive/negative review**
- Top **positive/negative sentiments** of users
- The **trending/shrinking words** 
- **Users' main cities**

## Screenshot <a name="screenshot"></a>

<table style="width:100%">
		<tr>
			<td><img src="https://github.com/blackeko/scrapeadvisor/blob/media/word_cloud.png" ></td>
			<td><img src="https://github.com/blackeko/scrapeadvisor/blob/media/common_words.png" ></td>
		</tr>
		<tr>
			<td><img src="https://github.com/blackeko/scrapeadvisor/blob/media/sent_afinn.png" ></td>
			<td><img src="https://github.com/blackeko/scrapeadvisor/blob/media/shrinking.png" ></td>
		</tr>
</table>

## Supported Languages <a name="languages"></a>

- English
- Italian

## Built Using <a name = "built_using"></a>

- [Kivy](https://kivy.org/#home) - GUI
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - HTML scraping 
- [R](https://www.r-project.org/about.html) - Sentiment Analysis


## Acknowledgements <a name = "acknowledgement"></a>

- [@susanli2016](https://github.com/susanli2016) - [Web Scraping TripAdvisor](https://towardsdatascience.com/scraping-tripadvisor-text-mining-and-sentiment-analysis-for-hotel-reviews-cc4e20aef333)
- [TextWiller](https://github.com/livioivil/TextWiller) - For providing Italian stop words and lexicon 
- All the other [packages](#about) - Thank you for being you

## Disclaimer

*Scrapeadvisor* is provided under this License on an AS-IS basis, **without warranty of any kind**, either expressed, implied, or statutory, including, without limitation, warranties that the *scrapeadvisor* is free of defects, merchantable, fit for a particular purpose or non-infringing.

To the extent permitted under Law, *scrapeadvisor* is provided under an AS-IS basis. The *scrapeadvisor* Team shall never, and without any limit, be liable for any damage, cost, expense or any other payment incurred as a result of *scrapeadvisor*'s actions, failure, bugs and/or any other interaction between *scrapeadvisor* and end-equipment, computers, other software or any 3rd party, end-equipment, computer or services.

We **do not encourage** running *scrapeadvisor* against Tripadvisor without prior mutual consent. The *scrapeadvisor* Team accept no liability and are not responsible for any misuse or damage caused by *scrapeadvisor*.
