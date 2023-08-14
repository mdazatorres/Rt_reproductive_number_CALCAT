#install.packages("INLA",repos=c(getOption("repos"),INLA="https://inla.r-inla-download.org/R/stable"), dep=TRUE)
library(INLA)
library(zoo) # moving averages
#library(tidyverse)
require(dplyr) # To manipulate data
library(tidyr)# To manipulate data
trim_fun = function(x){
  # remove NA
  x = x[!is.na(x)]
  if(length(x) <= 2){
    return(mean(x))
  } else{
    x1 = sort(x)
    x1 = x1[2:(length(x1)-1)] # Remove max values and min values
    return(mean(x1))
  }
}

data_full <- read.csv("output/data_ww_CA_county.csv")
head(data_full)

data_full <- data_full  %>% mutate(date  = as.Date(date))
# All counties
counties = unique(data_full$county)
# Columns names and new variables
variables = colnames(data_full)
added = c("Cases_N")
added2 = c("mean","sd", "0.025quant","0.5quant","0.975quant","mode")
all_col = c(variables,added,added2)
# Create the 
data_output = data.frame(matrix(NA,ncol = length(all_col)))
colnames(data_output) = all_col
data_output = data_output[-1,]
# Period of study
for(cty in counties){
  print(cty)
  data = data_full %>% filter(county == cty)   
  star_date = min(data$date); end_date = max(data$date)#"2022-12-31"#"2023-01-28"#"2023-02-11"#
  day_range <- seq(as.Date(star_date),as.Date(end_date),by="day")

  dates = data.frame(date=day_range) # Dats with no gaps
  #data = data %>% filter(date >= star_date & date <= end_date)
  data = merge(dates,data,by="date",all.x = T) # No gaps in the dates
  #data = data %>% mutate(N_av10 = rollapply(SC2_N_norm_PMMoV,width=10,trim_fun,align='right',fill=NA))#,
                         #N_r_av10 = rollapply(SC2_N_gc_g_dry_weight,width=10,trim_fun,align='right',fill=NA))
  delet_n = 10 # Remove the delet_n firts for the moving average
  data = data[-c(1:delet_n),]
  
  ################################################################################
  tm  <- 1:dim(data)[1] #data[,"time"] 
  y   <- log(data[,"SC2_N_norm_PMMoV"])
  #y = ifelse(y==-Inf,NA,y)
  ## fit the model
  formula = y~f(z,model="ar1")
  result = inla(formula,family="gaussian", data = list(y=y, z=tm))#, E=E)
  #summary(result)
  # Cases respect to minimum concentration
  wc = 1
  
  # expected log concetration
  yhat = exp(result$summary.fitted.values)
  kk = wc/min(yhat$mean[yhat$mean>0],na.rm=T) 
  data$Cases_N = kk * yhat$mean # Cases from INLA
  
  output = cbind(data,yhat)
  data_output = rbind(data_output,output)
}
write.csv(data_output, "output/data_ww_CA_county_ARIMA.csv")

#"output/cases_WW_0728.csv"

