# ipak function: install and load multiple R packages.
# check to see if packages are installed. Install them if they are not, then load them into the R session.

ipak <- function(pkg){
    new.pkg <- pkg[!(pkg %in% installed.packages()[, "Package"])]
    if (length(new.pkg)) 
        install.packages(new.pkg, dependencies = TRUE)
    sapply(pkg, require, character.only = TRUE)
}

# usage
packages <- c("dplyr","readr","lubridate","ggplot2","tidytext","tidyverse","stringr","tidyr","scales","broom","purrr",
				"widyr","igraph","ggraph","SnowballC","wordcloud","reshape2","TeachingDemos")
ipak(packages)