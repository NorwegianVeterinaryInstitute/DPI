FROM r-base:4.3.1

# DEPENDENCIES 
RUN apt-get update && apt-get install -y libssl-dev \
    libcurl4-openssl-dev libfontconfig1-dev libxml2-dev procps \
    pandoc libmariadb-dev libmagick++-dev libudunits2-dev \
    libharfbuzz-dev libfribidi-dev libgdal-dev libpq-dev \
    cargo

# R libraries
RUN R --slave -e 'install.packages("devtools")' 
RUN R --slave -e 'devtools::install_url("https://cran.r-project.org/src/contrib/tidyverse_2.0.0.tar.gz", dependencies = TRUE, upgrade = "always")'
RUN R --slave -e 'devtools::install_url("https://cran.r-project.org/src/contrib/logr_1.3.4.tar.gz", dependencies = TRUE, upgrade = "always")'
RUN R --slave -e 'devtools::install_url("https://cran.r-project.org/src/contrib/optparse_1.7.3.tar.gz", dependencies = TRUE, upgrade = "always")' 

# Environments
ENV LC_ALL=C
ENV PATH="$PATH:/usr/bin"
ENV R_LIBS_USER="/usr/local/lib/R/site-library:/usr/lib/R/site-library:/usr/lib/R/library:/usr/lib/R/lib"
