# Create a log log and commits ordered on size plot as done by Merelo

setwd("./output/csv")
.libPaths( c( .libPaths(), "~/Documents/R/win-library/3.6") )
print(.libPaths())
simulation.name <- 'WebAppRun'
print('Found R script')
## ----setup, cache=FALSE,echo=FALSE,warning=FALSE,message=FALSE-----------
library(ggplot2, lib.loc='~/Documents/R/win-library/3.6')
library("ggfortify", lib.loc='~/Documents/R/win-library/3.6')
library(ggthemes, lib.loc='~/Documents/R/win-library/3.6') # package ‘ggthemes’’ is not available (for R version 3.5.0)
library(dplyr, lib.loc='~/Documents/R/win-library/3.6')
library(TTR, lib.loc='~/Documents/R/win-library/3.6')
library(xtable, lib.loc='~/Documents/R/win-library/3.6')

amount_of_simulations = 1
#use 
# set the location of the result files
pref <- ''
# give the names of the result files excluding .csv
files = './commits'
# name the files
urls <- files
# name of the languages in which the prjects were written
language <- 'java'

age <-  data.frame(Name = character(),
                   file = character(),
                   language = character(),
                   age = integer(),
                   Median = double(),
                   Mean = double(),
                   SD = double())
url.list <- list()
# put together the data and additional information
for (i in 1:length(files) ) {
  file.name = paste0(pref,files[i],'.csv')
  these.lines <-  read.csv(file.name)
  url.list[[file.name]] <- urls[i]
  age <- rbind( age,
                data.frame(Name = urls[i],
                           file = file.name,
                           language = language,
                           age = length(these.lines$colummn),
                           Median =  as.double(median(these.lines$colummn)),
                           Mean = as.double(mean(these.lines$colummn)),
                           SD = as.double(sd(these.lines$colummn) )))
}
# produce an oversight summary of the of the mean median and standard deviation 
summary <- age[order(age$age),]
lines <- list()
# Read again in order because I am useless in R
for (i in 1:length(summary$file) ) {
  lines[[i]] <-  read.csv(as.character(age$file[i]))
  lines[[i]]$url <- url.list[[summary[[i,'file']]]]
  lines[[i]]$SMA10 <- SMA(lines[[i]]$colummn,n=10)
  lines[[i]]$SMA20 <- SMA(lines[[i]]$colummn,n=20)
}

## ----linecount,message=FALSE, fig.subcap=summary$Name, echo=FALSE,warning=FALSE,fig.height=4,out.width='.245\\linewidth'----
sizes.fit.df <- data.frame(Name = character(),
                           Coefficient = double(),
                           Intercept = double())
for (i in 1:length(lines) ) {
  by.lines <- group_by(lines[[i]],colummn)
  lines.count <- summarize(by.lines, count=n())
  sizes.fit <- lm(log(1+lines.count$colummn) ~ log(lines.count$count))
  repo <- strsplit(paste(summary[[1]][i],""),"_",fixed=T)
  sizes.fit.df <- rbind( sizes.fit.df,
                         data.frame( Name = repo[[1]][1],
                                     Intercept = summary(sizes.fit)$coefficients[1],
                                     Coefficient = summary(sizes.fit)$coefficients[2] ))
  ggplot(lines.count, aes(x=colummn, y=count))+geom_point()+scale_x_log10()+scale_y_log10()+stat_smooth() +
    ggtitle(lines[[i]]$url) + xlab("Commit size") + ylab("Frequency") + 
    theme(
      legend.position="none", 
      plot.title = element_text(color="white"),
      axis.title.x = element_text(color="white"),
      axis.title.y = element_text(color="white"),
      plot.background = element_rect(fill = "black", color = NA), # bg of the plot,
      axis.text.x = element_text( color = "white"),
      axis.text.y = element_text( color = "white")
    )
  
  lines[[i]]$repo = gsub("/","_",trimws(repo[[1]][1]))
  ggsave(paste0("../../web_output/powerlaw.png"),device='png')
}
