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
library(TextWiller)
library(TeachingDemos)
library(rworldmap)
theme_set(theme_minimal()) 


# load file of sentiments
sentiments <- read_csv("Rinput/sent.csv")
load(file = "Rinput/itastopwords.rda")


# read the CSV file
df <- read_csv(filename)
Sys.setlocale("LC_TIME", "C")
df$review_date <- as.Date(df$review_date,format = "%B %d, %Y")
setwd("Routput")
txtStart("out.txt", commands=FALSE, results=TRUE, append=FALSE, visible.only=FALSE)
print("it")
dim(df); min(df$review_date); max(df$review_date)
txtStop()

# number reviews per week
png("rev_per_week.png", width = 1920, height = 1080, res=300)
df %>%
  count(Week = round_date(review_date, "week")) %>%
  ggplot(aes(Week, n)) +
  geom_line() + 
  ggtitle('Numero di recensioni per settimana') + 
  labs(x = "Settimana",
       y = "Numero recensioni")
  dev.off()

# most common word stemmed
df <- tibble::rowid_to_column(df, "ID")
df <- df %>%
  mutate(review_date = as.POSIXct(review_date, origin = "1970-01-01"),month = round_date(review_date, "month"))


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


stopword <- tibble(word=itastopwords)

review_words <- df %>%
  distinct(review_body, .keep_all = TRUE) %>%
  unnest_tokens(word, review_body, token="regex", pattern="[\\s\\.\\,\\-\\;\\:\\_\\?\\!\\'\\\"\\/\\(\\)\\[\\]\\{\\}\\+\\=\\<\\>\\$\\???]+") %>%
  distinct(ID, word, .keep_all = TRUE) %>%
  anti_join(stopword, by = "word") %>% #removes Italian stepwords
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

# 25 most common words
png("25_most_common_words.png", width = 1920, height = 1080, res=300)
word_counts %>%
  head(25) %>%
  mutate(word = wordStem(word, "it")) %>% 
  mutate(word = reorder(word, n)) %>%
  ggplot(aes(word, n)) +
  geom_col(fill = "lightblue") +
  scale_y_continuous(labels = comma_format()) +
  coord_flip() +
  labs(title = "Parole maggiormente utilizzate",
       subtitle = "Stop word rimosse, stemming delle parole",
       x = "Parola",
       y = "Numero di occorrenze")
  dev.off()

# biagrams
review_bigrams <- df %>%
  unnest_tokens(bigram, review_body, token = "ngrams", n = 2)

bigrams_separated <- review_bigrams %>%
  separate(bigram, c("word1", "word2"), sep = " ")

bigrams_filtered <- bigrams_separated %>%
  filter(!word1 %in% stopword$word) %>%
  filter(!word2 %in% stopword$word)

bigram_counts <- bigrams_filtered %>% 
  count(word1, word2, sort = TRUE)

bigrams_united <- bigrams_filtered %>%
  unite(bigram, word1, word2, sep = " ")

txtStart("out.txt", commands=FALSE, results=TRUE, append=TRUE, visible.only=FALSE)
bigrams_united %>%
  count(bigram, sort = TRUE)  %>%
  head(10) # display only first 10 results
txtStop()


# trigrams
review_trigrams <- df %>%
  unnest_tokens(trigram, review_body, token = "ngrams", n = 3)

trigrams_separated <- review_trigrams %>%
  separate(trigram, c("word1", "word2", "word3"), sep = " ")

trigrams_filtered <- trigrams_separated %>%
  filter(!word1 %in% stopword$word) %>%
  filter(!word2 %in% stopword$word) %>%
  filter(!word3 %in% stopword$word)

trigram_counts <- trigrams_filtered %>% 
  count(word1, word2, word3, sort = TRUE)

trigrams_united <- trigrams_filtered %>%
  unite(trigram, word1, word2, word3, sep = " ")

txtStart("out.txt", commands=FALSE, results=TRUE, append=TRUE, visible.only=FALSE)
trigrams_united %>%
  count(trigram, sort = TRUE) %>%
  head(10) # display only first 10 results
txtStop()



# increasing words per months
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
  labs(x = "Anno",
       y = "Percentuale di recensioni contenenti questa parola",
       title = "Parole che sono cresciute maggiormente")
  dev.off()

# decreasing word per month
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
  labs(x = "Anno",
       y = "Percentuale di recensioni contenenti questa parola",
       title = "Parole che sono diminuite maggiormente")
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
  anti_join(stopword, by="word")

stemmed <- tidy_reviews %>%
  mutate(word = wordStem(word, "it"))

contributions <- stemmed %>%
  inner_join(sentiments, by = "word") %>%
  group_by(word) %>%
  summarize(occurences = n(), contribution = sum(score))

png("sent_afinn.png", width = 1920, height = 1080, res=300)
contributions %>%
  top_n(20, abs(contribution)) %>%
  mutate(word = reorder(word, contribution)) %>%
  ggplot(aes(word, contribution, fill = contribution > 0)) +
  ggtitle('Parole piu connesse a sentimenti positivi/negativi') +
  xlab("Parola") +
  ylab("Numero di occorrenze") +
  geom_col(show.legend = FALSE) +
  coord_flip()
  dev.off()


# preceeded by not
bigrams_filtered %>%
  filter(word1 == "non") %>%
  count(word1, word2, sort = TRUE)

not_words <- trigrams_filtered %>%
  filter(word1 == "non") %>%
  inner_join(sentiments, by = c(word2 = "word")) %>%
  count(word2, score, sort = TRUE) %>%
  ungroup()

# negation with no, not, never and without
negation_words <- c("non", "no", "ne", "neppure", "neanche", "nemmeno", "mai", "senza")


negated_words <- bigrams_filtered %>%
  filter(word1 %in% negation_words) %>%
  #inner_join(sentiments, by = c(word2 = "word")) %>% eheheh
  count(word1, word2, sort = TRUE) %>%
  ungroup()

negated_words %>% head(10)


png("25_not_follows.png", width = 1920, height = 1080, res=300)
negated_words %>%
  head(25) %>%
  mutate(word = reorder(paste(word1,word2, sep=" "), n)) %>%
  ggplot(aes(word, n)) +
  geom_col(fill = "brown1") +
  scale_y_continuous(labels = comma_format()) +
  coord_flip() +
  labs(title = "Parole seguite da negazioni",
       x = "Parola",
       y = "Numero di occorrenze")
dev.off()


# with contributions of sentiments
negated_words_sent <- bigrams_filtered %>%
  filter(word1 %in% negation_words) %>%
  inner_join(sentiments, by = c(word2 = "word")) %>% 
  count(word1, word2, score, sort = TRUE) %>%
  ungroup()


x <- tryCatch(eval(parse(text = '
file.create("not_follows.png")
png("not_follows.png", width = 1920, height = 1080, res=300)
negated_words_sent %>%
  mutate(contribution = n * score,
         word2 = reorder(paste(word2, word1, sep = "__"), contribution)) %>%
  group_by(word1) %>%
  top_n(12, abs(contribution)) %>%
  ggplot(aes(word2, contribution, fill = n * score > 0)) +
  geom_col(show.legend = FALSE) +
  facet_wrap(~ word1, scales = "free") +
  scale_x_discrete(labels = function() gsub("__.+$", "", x)) +
  xlab("Word") +
  ylab("Score") +
  coord_flip()')), error = function(e) e)

# here we have a permission denied error.. lol
tryCatch(print(x), error = function(e) file.remove("not_follows.png"))

# lastly, let's find out the most positive and negative reviews
sentiment_messages <- stemmed %>%
  inner_join(sentiments, by = "word") %>%
  group_by(ID) %>%
  summarize(sentiment = mean(score), words = n()) %>%
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

