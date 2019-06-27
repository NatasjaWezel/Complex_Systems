# Create a log log and commits ordered on size plot as done by Merelo

setwd("/Users/koengreuell/Documents/1819css/sourcetree/Analysis")
simulation.name <- readline(prompt="Enter simulation name: ")

multiplot <- function(..., plotlist=NULL, file, cols=1, layout=NULL) {
  require(grid)
  
  # Make a list from the ... arguments and plotlist
  plots <- c(list(...), plotlist)
  
  numPlots = length(plots)
  
  # If layout is NULL, then use 'cols' to determine layout
  if (is.null(layout)) {
    # Make the panel
    # ncol: Number of columns of plots
    # nrow: Number of rows needed, calculated from # of cols
    layout <- matrix(seq(1, cols * ceiling(numPlots/cols)),
                     ncol = cols, nrow = ceiling(numPlots/cols))
  }
  
  if (numPlots==1) {
    print(plots[[1]])
    
  } else {
    # Set up the page
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(nrow(layout), ncol(layout))))
    
    # Make each plot, in the correct location
    for (i in 1:numPlots) {
      # Get the i,j matrix positions of the regions that contain this subplot
      matchidx <- as.data.frame(which(layout == i, arr.ind = TRUE))
      
      print(plots[[i]], vp = viewport(layout.pos.row = matchidx$row,
                                      layout.pos.col = matchidx$col))
    }
  }
}

## ----setup, cache=FALSE,echo=FALSE,warning=FALSE,message=FALSE-----------
library(ggplot2)
library("ggfortify")
library(ggthemes) # package ‘ggthemes’’ is not available (for R version 3.5.0)
library(dplyr)
library(TTR)
library(xtable)

amount_of_simulations = 60
#use 
# set the location of the result files
pref <- 'simulation_results/'
# give the names of the result files excluding .csv
files <- c()
# REDUCE PLOTS

for (i in 0:9){#(amount_of_simulations-1)){
  files = append(files,paste0('commit_list',i,simulation.name))
}

# name the files
urls <- files
# name of the languages in which the projects were written
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
     xlab("Commit size") + ylab("Frequency") + 
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
  ggsave(paste0("figure/",simulation.name,lines[[i]]$url,"-linecount-.png"),device='png')
}

if (FALSE){
## ----powerlaw,message=FALSE, fig.subcap=summary$Name,echo=FALSE,warning=FALSE,fig.height=4,out.width='.115\\linewidth'----
zipf.fit.df <- data.frame(Name = character(),
                          Coefficient = double(),
                          Intercept = double())
for (i in 1:length(lines) ) {
  sorted.lines <- data.frame(x=1:length(lines[[i]]$colummn),colummn=as.numeric(lines[[i]][order(-lines[[i]]$colummn),]$colummn))
  ggplot()+geom_point(data=sorted.lines,aes(x=x,y=colummn))+scale_y_log10()+ggtitle(lines[[i]]$url)+
    theme(
      legend.position="none", 
      plot.title = element_text(color="white"),
      axis.title.x = element_text(color="white"),
      axis.title.y = element_text(color="white"),
      plot.background = element_rect(fill = "black", color = NA), # bg of the plot,
      axis.text.x = element_text( color = "white"),
      axis.text.y = element_text( color = "white")
    )
  ggsave(paste0("figure/",simulation.name,"powerlaw-",lines[[i]]$repo,".png"),device='png')
  sorted.lines.no0 <- sorted.lines[sorted.lines$colummn>0,]
  repo <- strsplit(paste(summary[[1]][i],""),"_")
  zipf.fit <- lm(log(sorted.lines.no0$colummn) ~ sorted.lines.no0$x)
  zipf.fit.df <- rbind( zipf.fit.df,
                        data.frame( Name = repo[[1]][1],
                                    Intercept = summary(zipf.fit)$coefficients[1],
                                    Coefficient = summary(zipf.fit)$coefficients[2] ))
}



## ----autocorrelation,message=FALSE, cache=FALSE,echo=FALSE,fig.height=4,fig.subcap=summary$Name,out.width='.115\\linewidth'----
for (i in 1:length(lines) ) {
  autoplot(pacf(lines[[i]]$colummn, plot=FALSE,xlab="some name")) + theme(
    legend.position="none", 
    plot.title = element_text(color="white"),
    axis.title.x = element_text(color="white"),
    axis.title.y = element_text(color="white"),
    plot.background = element_rect(fill = "black", color = NA), # bg of the plot,
    axis.text.x = element_text( color = "white"),
    axis.text.y = element_text( color = "white")
  )
  
  ggsave(paste0("figure/",simulation.name,"-auto-",lines[[i]]$repo,".png"),device='png')
}

## ----spectrum,message=FALSE, cache=FALSE,echo=FALSE,fig.height=4,fig.subcap=summary$Name,out.width='.245\\linewidth'----
spec.fit.df <- data.frame(Name = character(),
                          Coefficient = double(),
                          p = double())
for (i in 1:length(lines) ) {
  this.spectrum <- spectrum(lines[[i]]$colummn, plot=FALSE)
  autoplot( this.spectrum ) + scale_x_log10() + theme(legend.position="none",axis.title.x=element_blank(),axis.title.y=element_blank()) +
    ggtitle(lines[[i]]$url)+
    theme(
      legend.position="none", 
      plot.title = element_text(color="white"),
      axis.title.x = element_text(color="white"),
      axis.title.y = element_text(color="white"),
      plot.background = element_rect(fill = "black", color = NA), # bg of the plot,
      axis.text.x = element_text( color = "white"),
      axis.text.y = element_text( color = "white")
    )
  ggsave(paste0("figure/",simulation.name,"-pinknoise-",lines[[i]]$repo,".png"),device='png')
  spec.fit <- lm(log(this.spectrum$spec) ~ log(this.spectrum$freq**2))
  repo <- strsplit(paste(summary[[1]][i],""),"_")
  f <- summary(spec.fit)$fstatistic
  p <- pf(f[1],f[2],f[3],lower.tail=F)
  attributes(p) <- NULL
  spec.fit.df <- rbind( spec.fit.df,
                        data.frame( Name = repo[[1]][1],
                                    p = p,
                                    Coefficient = summary(spec.fit)$coefficients[2] ))
}
}
