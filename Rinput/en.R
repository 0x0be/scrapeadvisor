#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)
args <- commandArgs(TRUE)
filename <- as.character(args[1])
library(dplyr)
library(readr)
library(lubridate)
library(ggplot2)
library(tidytext)
library(tidyverse)
library(stringr)
library(tidyr)
library(scales)
library(broom)
library(purrr)
library(widyr)
library(igraph)
library(ggraph)
library(SnowballC)
library(wordcloud)
library(reshape2)
library(TeachingDemos)
library(rworldmap)
theme_set(theme_minimal())


# min & max date
df <- read_csv(filename)
#df <- df[complete.cases(df), ] # remove row if one of the attr value is NA
Sys.setlocale("LC_TIME", "C")
df$review_date <- as.Date(df$review_date,format = "%B %d, %Y")
setwd("Routput")
txtStart("out.txt", commands=FALSE, results=TRUE, append=FALSE, visible.only=FALSE)
print("en")
dim(df); min(df$review_date); max(df$review_date)
txtStop()

# numbers rev per week
png("rev_per_week.png", width = 1920, height = 1080, res=300)
df %>%
  count(Week = round_date(review_date, "week")) %>%
  ggplot(aes(Week, n)) +
  geom_line() + 
  ggtitle('The Number of Reviews Per Week')
  dev.off()

  
# most common words
df <- tibble::rowid_to_column(df, "ID")
df <- df %>%
  mutate(review_date = as.POSIXct(review_date, origin = "1970-01-01"), month = round_date(review_date, "month"))


# locations
locations <- df %>%
  group_by(user_location) %>%
  summarise(count = length(user_location))

# cities and States
locations <- locations %>%
  separate(user_location, into = c("city", "state"), sep = ", ")



# top 10 cities
top_cities <- arrange(locations, desc(count))

txtStart("out.txt", commands=FALSE, results=TRUE, append=TRUE, visible.only=FALSE)
print("cities")
top_cities %>%
  select(city, count) %>%
  group_by(city) %>%
  head(10)
txtStop()


# top 10 States
top_states <- locations %>% 
  group_by(state) %>% 
  summarise(count = sum(count))

top_states <- arrange(top_states, desc(count))

txtStart("out.txt", commands=FALSE, results=TRUE, append=TRUE, visible.only=FALSE)
print("states")
top_states %>%
  head(10)
txtStop()



# world map
#png("world_map.png", width = 1920, height = 1080, res=300)
#matched <- joinCountryData2Map(top_states, joinCode="NAME", nameJoinColumn="state")
#tryCatch(mapCountryData(matched, nameColumnToPlot="state", mapTitle="User Location Distribution", catMethod = "pretty", colourPalette = "heat"), error = function(e) print(e))
#dev.off()

review_words <- df %>%
  distinct(review_body, .keep_all = TRUE) %>%
  unnest_tokens(word, review_body, token="regex", pattern="[\\s\\.\\,\\-\\;\\:\\_\\?\\!\\'\\\"\\/\\(\\)\\[\\]\\{\\}\\+\\=\\<\\>\\$\\???]+",drop = FALSE) %>%
  distinct(ID, word, .keep_all = TRUE) %>%
  anti_join(stop_words, by = "word") %>%
  filter(str_detect(word, "[^\\d]")) %>%
  group_by(word) %>%
  mutate(word_total = n()) %>%
  ungroup()

# most common words with wordclouds
png("25_wordclouds.png", width = 1920, height = 1080, res=300)
word_counts <- review_words %>%
  count(word, sort = TRUE) %>%
  with(wordcloud(word, n, max.words = 50))
  dev.off()

word_counts <- review_words %>%
  count(word, sort = TRUE) 


png("25_most_common_words.png", width = 1920, height = 1080, res=300)
word_counts %>%
  head(25) %>%
  mutate(word = wordStem(word)) %>% 
  mutate(word = reorder(word, n)) %>% 
  ggplot(aes(word, n)) +
  geom_col(fill = "lightblue") +
  scale_y_continuous(labels = comma_format()) +
  coord_flip() +
  labs(title = "Most common words in reviews to date",
       subtitle = "Stop words removed and stemmed",
       y = "Number of uses")
  dev.off()




# bigrams
review_bigrams <- df %>%
  unnest_tokens(bigram, review_body, token = "ngrams", n = 2)

bigrams_separated <- review_bigrams %>%
  separate(bigram, c("word1", "word2"), sep = " ")

bigrams_filtered <- bigrams_separated %>%
  filter(!word1 %in% stop_words$word) %>%
  filter(!word2 %in% stop_words$word)

bigram_counts <- bigrams_filtered %>% 
  count(word1, word2, sort = TRUE)

bigrams_united <- bigrams_filtered %>%
  unite(bigram, word1, word2, sep = " ")

txtStart("out.txt", commands=FALSE, results=TRUE, append=TRUE, visible.only=FALSE)
bigrams_united %>%
  count(bigram, sort = TRUE) %>%
  head(10)
txtStop()



# trigrams
review_trigrams <- df %>%
  unnest_tokens(trigram, review_body, token = "ngrams", n = 3)

trigrams_separated <- review_trigrams %>%
  separate(trigram, c("word1", "word2", "word3"), sep = " ")

trigrams_filtered <- trigrams_separated %>%
  filter(!word1 %in% stop_words$word) %>%
  filter(!word2 %in% stop_words$word) %>%
  filter(!word3 %in% stop_words$word)

trigram_counts <- trigrams_filtered %>% 
  count(word1, word2, word3, sort = TRUE)

trigrams_united <- trigrams_filtered %>%
  unite(trigram, word1, word2, word3, sep = " ")

txtStart("out.txt", commands=FALSE, results=TRUE, append=TRUE, visible.only=FALSE)
trigrams_united %>%
  count(trigram, sort = TRUE) %>%
  head(10)
txtStop()




# growing reviews
reviews_per_month <- df %>%
  group_by(month) %>%
  summarize(month_total = n())

word_month_counts <- review_words %>%
  filter(word_total >= 10) %>%
  count(word, month) %>%
  tidyr::complete(word, month, fill = list(n = 0)) %>%
  inner_join(reviews_per_month, by = "month") %>%
  mutate(percent = n / month_total) %>%
  mutate(year = year(month) + yday(month) / 365)



mod <- ~ glm(cbind(n, month_total - n) ~ year, ., family = "binomial")

slopes <- word_month_counts %>%
  nest(-word) %>%
  mutate(model = map(data, mod)) %>%
  unnest(map(model, tidy)) %>%
  filter(term == "year") %>%
  arrange(desc(estimate))


png("9_growing.png", width = 1920, height = 1080, res=300)
slopes %>%
  head(9) %>%
  inner_join(word_month_counts, by = "word") %>%
  mutate(word = reorder(word, -estimate)) %>%
  ggplot(aes(month, n / month_total, color = word)) +
  geom_line(show.legend = FALSE) +
  scale_y_continuous(labels = percent_format()) +
  facet_wrap(~ word, scales = "free_y") +
  expand_limits(y = 0) +
  labs(x = "Year",
       y = "Percentage of reviews containing this word",
       title = "9 fastest growing words in TripAdvisor reviews")
  dev.off()


# decreasing
png("9_decreasing.png", width = 1920, height = 1080, res=300)
slopes %>%
  tail(9) %>%
  inner_join(word_month_counts, by = "word") %>%
  mutate(word = reorder(word, estimate)) %>%
  ggplot(aes(month, n / month_total, color = word)) +
  geom_line(show.legend = FALSE) +
  scale_y_continuous(labels = percent_format()) +
  facet_wrap(~ word, scales = "free_y") +
  expand_limits(y = 0) +
  labs(x = "Year",
       y = "Percentage of reviews containing this term",
       title = "9 fastest shrinking words in TripAdvisor reviews")
  dev.off()


# SENTIMENT ANALYSIS
# most common positive and negative words
reviews <- df %>% 
  filter(!is.na(review_body)) %>% 
  select(ID, review_body) %>% 
  group_by(row_number()) %>% 
  ungroup()
tidy_reviews <- reviews %>%
  unnest_tokens(word, review_body, token="regex", pattern="[\\s\\.\\,\\-\\;\\:\\_\\?\\!\\'\\\"\\/\\(\\)\\[\\]\\{\\}\\+\\=\\<\\>\\$\\???]+") 
  
tidy_reviews <- tidy_reviews %>%
  anti_join(stop_words, by="word")

bing_word_counts <- tidy_reviews %>%
  inner_join(get_sentiments("bing"), by="word") %>%
  count(word, sentiment, sort = TRUE) %>%
  ungroup()

png("sent_bing.png", width = 1920, height = 1080, res=300)
bing_word_counts %>%
  group_by(sentiment) %>%
  top_n(10, n) %>%
  ungroup() %>%
  mutate(word = reorder(word, n)) %>%
  ggplot(aes(word, n, fill = sentiment)) +
  geom_col(show.legend = FALSE) +
  facet_wrap(~sentiment, scales = "free") +
  labs(y = "Contribution to sentiment", x = NULL) +
  coord_flip() + 
  ggtitle('Words with the greatest contributions to positive/negative 
          sentiment in reviews [BING]') +
  geom_col(show.legend = FALSE)
  dev.off()

# AFINN library
png("sent_afinn.png", width = 1920, height = 1080, res=300)
contributions <- tidy_reviews %>%
  inner_join(get_sentiments("afinn"), by = "word") %>%
  group_by(word) %>%
  summarize(occurences = n(), contribution = sum(score))
  contributions %>%
  top_n(20, abs(contribution)) %>%
  mutate(word = reorder(word, contribution)) %>%
  ggplot(aes(word, contribution, fill = contribution > 0)) +
  ggtitle('Words with the greatest contributions to positive/negative 
          sentiment in reviews [AFINN]') +
  geom_col(show.legend = FALSE) +
  coord_flip()
  dev.off()


# preceeded by not
bigrams_separated %>%
  filter(word1 == "not") %>%
  count(word1, word2, sort = TRUE)

AFINN <- get_sentiments("afinn")
not_words <- bigrams_separated %>%
  filter(word1 == "not") %>%
  inner_join(AFINN, by = c(word2 = "word")) %>%
  count(word2, score, sort = TRUE) %>%
  ungroup()


not_words %>%
  mutate(contribution = n * score) %>%
  arrange(desc(abs(contribution))) %>%
  head(20) %>%
  mutate(word2 = reorder(word2, contribution)) %>%
  ggplot(aes(word2, n * score, fill = n * score > 0)) +
  geom_col(show.legend = FALSE) +
  xlab("Words preceded by \"not\"") +
  ylab("Sentiment score * number of occurrences") +
  ggtitle('The 20 words preceded by "not" that had the greatest contribution to 
          sentiment scores, positive or negative direction') +
  coord_flip()


# negation with no, not, never and without
negation_words <- c("not", "no", "never", "without")

negated_words <- bigrams_separated %>%
  filter(word1 %in% negation_words) %>%
  inner_join(AFINN, by = c(word2 = "word")) %>%
  count(word1, word2, score, sort = TRUE) %>%
  ungroup()

png("not_follows.png", width = 1920, height = 1080, res=300)
negated_words %>%
  mutate(contribution = n * score,
         word2 = reorder(paste(word2, word1, sep = "__"), contribution)) %>%
  group_by(word1) %>%
  top_n(12, abs(contribution)) %>%
  ggplot(aes(word2, contribution, fill = n * score > 0)) +
  geom_col(show.legend = FALSE) +
  facet_wrap(~ word1, scales = "free") +
  scale_x_discrete(labels = function(x) gsub("__.+$", "", x)) +
  xlab("Words preceded by negation term") +
  ylab("Sentiment score * number of occurrences") +
  ggtitle('The most common positive and negative words which follow negations 
          such as "no", "not", "never" and "without"') +
  coord_flip()
  dev.off()



# lastly, let's find out the most positive and negative reviews
sentiment_messages <- tidy_reviews %>%
  inner_join(get_sentiments("afinn"), by = "word") %>%
  group_by(ID) %>%
  summarize(sentiment = mean(score),
            words = n()) %>%
  ungroup() %>%
  filter(words >= 5)

# most positive reviews
sentiment_messages %>%
  arrange(desc(sentiment)) %>%
  head(1) -> i
txtStart("out.txt", commands=FALSE, results=TRUE, append=TRUE, visible.only=FALSE)
print("pos_rev")
df[ which(df$ID==i$ID), ]$review_body[1]
txtStop()

# most negative reviews
sentiment_messages %>%
  arrange(sentiment) %>%
  head(1) -> i
txtStart("out.txt", commands=FALSE, results=TRUE, append=TRUE, visible.only=FALSE)
print("neg_rev")
df[ which(df$ID==i$ID), ]$review_body[1]
txtStop()
  
