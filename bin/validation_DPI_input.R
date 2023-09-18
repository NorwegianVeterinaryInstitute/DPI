# Setup 
library(tidyverse)
library(here)

# input 
sample_sheet_file <- here::here("20230914_DPI_samples.csv")




# Rscript  ----
sample_sheet <- readr::read_csv(sample_sheet_file) 
dim(sample_sheet)

sample_sheet_unique_pairs <- 
  sample_sheet %>%
  dplyr::rowwise() %>%
  dplyr::mutate(pairs = str_c(sort(c(sample1, sample2)), collapse = "_")) %>%
  dplyr::ungroup() %>%
  dplyr::distinct(pairs, .keep_all = T) %>%
  dplyr::select(-pairs)


dim(sample_sheet) 
dim(sample_sheet_unique_pairs)

write_csv(sample_sheet_unique_pairs, 
          "20230914_DPI_samples_unique_pairs.csv")  


  