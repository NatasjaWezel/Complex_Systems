# powerlaw bootstrapping to determine p_values_,xmin_values & alfa_values

setwd('/Users/koengreuell/Documents/1819css/sourcetree/Analysis/')
number_of_simulations = 100
#!/usr/bin/Rscript
# Import poweRlaw library
library(poweRlaw)

# declaring vectors used
repo_names <- c()
for (i in 0:9){#(amount_of_simulations-1)){
  repo_names = c(repo_names,paste0('simulation',i))
}
xmin_values_ <- c()
alfa_values_ <- c()
p_values_ <- c()

# Analysis for repos
for (repo_name in repo_names){
  repo = paste("../model/simulated_data/",repo_name,".csv",sep="")
  data_ <- read.csv(repo) # import data
  data_ <- data_$Lines.changed # remove commit numbers
  data_ <- data_[data_>0] # erase commits with 0 changes
  final_data = data.matrix(data_) # Update vector type
  m_m = displ$new(final_data) # Declare fit object
  est=estimate_xmin(m_m) # Estimate x_min
  m_m$setXmin(est) # Set x_min as calculated
  est_1=estimate_pars(m_m) # estimate parameters
  bs_p = bootstrap_p(m_m, no_of_sims=number_of_simulations, threads=15) #Execute bootstrapin to test powerlaw hypotehsis.
  p_values_ <- c(p_values_, bs_p$p) # add values to a vector
  xmin_values_ <- c(xmin_values_, est$xmin) 
  alfa_values_ <- c(alfa_values_, est$pars)
} 

final_dataframe <- data.frame(repo_names,p_values_,xmin_values_,alfa_values_) # add all  information to a dataframe
write.csv(final_dataframe, file="P-values_KStest.csv") # create a file with it.
