#!/usr/bin/env Rscript
# Description : Check input file, controls that no duplicates and organize single pairs for running efficiently.
# Author : Eve Zeyl Fiskebeck
# Version: 2023-09-29
# Usage:  Rscript <script_name> --input <input> | --version <TRUE/FALSE[Default]>

# Packages ----
if (!require("optparse")) {
  install.packages("optparse", dependencies = T) 
}
if (!require("tidyverse")) {
  install.packages("tidyverse", dependencies = T) 
}
if (!require("logr")) {
  install.packages("logr", dependencies = T) 
}


# Command ----

option_list = list(
  make_option("--input", action="store", 
              default="",
              type='character',
              help="The csv input file"),
  make_option("--version", action="store", 
              default= FALSE,
              type='logical',
              help="output version and quit")
)

opt = parse_args(OptionParser(option_list=option_list))

# Test 
#opt <-list()
#opt$input <- "input_pairs_20SNPs.csv"
#opt$input <- ""
#opt$version <- TRUE

# Code ---- 
# user provided input 

# Creating a log  
# https://logr.r-sassy.org/articles/logr.html
log_file <- "input_check.log"
logr::log_open(log_file, logdir = FALSE, autolog = TRUE)

if (opt$input == ""){
  
  # exmpty input
  # exporting session info
  if (opt$version) {
    # creating version dump
    version_file <- "input_check.version"
    sink(version_file, append = TRUE)
    cat("input_check.R version 1. date: 2023-09-29\n\n")
    cat("Session Info:\n\n")
    print(sessionInfo())
    sink()
  }
  else { logr::log_print("Cannot read your input file. Please recheck the format")}
  } else {

  input <- readr::read_csv(opt$input)
  
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

}
logr::log_close()




