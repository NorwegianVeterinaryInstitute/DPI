# Setup ----
library(pacman)
p_load(tidyverse, logr)

# Creating a log  and version dump
log_file <- "input_check.log"
version_file <- "input_check.version"

# https://logr.r-sassy.org/articles/logr.html
logr::log_open(log_file, logdir = FALSE, autolog = TRUE)

# Test ----
#input_file <- ""


# Script ---
# Usage: Rscript <scriptname> <input> 
args = commandArgs(trailingOnly = TRUE)
input <- args[1]

# user provided input 
input <- readr::read_csv(input_file)

logr::log_print("creating a dataframe of unique isolates and corresponding paths")
unique_samples_df <- 
  tibble::tibble(sample = c(input$sample1, input$sample2),
                 path = c(input$path1, input$path2)) %>%
  dplyr::distinct() 
          

logr::log_print("creating a dataframe of unique iunique pairs to compare")
unique_pairs_df <- 
  input %>%
    dplyr::rowwise() %>%
    dplyr::mutate(
      pair = stringr::str_c(sort(c(sample1, sample2)), collapse = "_")) %>%
    dplyr::ungroup() %>% 
    dplyr::distinct(pair,.keep_all = TRUE)


logr::log_print("exporting table of unique pairs: unique_pairs.csv")  
readr::write_csv(unique_pairs_df, "unique_pairs.csv")

logr::log_print("exporting table of unique samples-paths: unique_samples.csv")  
readr::write_csv(unique_samples_df, "unique_samples.csv")


logr::log_print("Exporting session info into input_check.version")  
logr::log_close()

# exporting session info
logr::log_open(version_file, logdir = FALSE, autolog = TRUE)
logr::log_print(sessionInfo())
logr::log_close()

