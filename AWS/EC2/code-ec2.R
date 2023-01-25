library(furrr)
library(purrr)
library(tidyverse)
library(tictoc)

by_gear <- mtcars %>%
  group_split(gear) 

plan(multisession, workers = 2)

models <- future_map(by_gear, ~lm(mpg ~ cyl + hp + wt, data = .))

# A t2.micro AWS instance
# Created from http://www.louisaslett.com/RStudio_AMI/
public_ip <- "3.84.236.202"

# This is where my pem file lives (password file to connect).
ssh_private_key_file <- "TEE2R-V2.pem"

connect_to_ec2 <- function(public_ip, ssh_private_key_file) {
  makeClusterPSOCK(
    
    # Public IP number of EC2 instance
    workers = public_ip,
    
    # User name (always 'ubuntu')
    user = "ubuntu",
    
    # Use private SSH key registered with AWS
    rshopts = c(
      "-o", "StrictHostKeyChecking=no",
      "-o", "IdentitiesOnly=yes",
      "-i", ssh_private_key_file
    ),
    
    rscript_args = c(
      # Set up .libPaths() for the 'ubuntu' user
      "-e", shQuote(paste0(
        "local({",
        "p <- Sys.getenv('R_LIBS_USER'); ",
        "dir.create(p, recursive = TRUE, showWarnings = FALSE); ",
        ".libPaths(p)",
        "})"
      )),
      # Install furrr
      "-e", shQuote("install.packages('furrr')")
    ),
    
    # Switch this to TRUE to see the code that is run on the workers without
    # making the connection
    dryrun = FALSE
  )
}

cl <- connect_to_ec2(public_ip, ssh_private_key_file)

cl

plan(cluster, workers = cl)

models <- future_map(by_gear, ~lm(mpg ~ cyl + hp + wt, data = .))

models

# Revert back to a sequential plan
plan(sequential)

parallel::stopCluster(cl)


func <- function(tempo, indice) {
  Sys.sleep(tempo)
  str_c("Replicação ", indice, ": ", Sys.time())
}

# Definindo os parâmetros sobre os quais queremos calcular a função
time_sleep <- rep(10, 6)

# Definindo a precisão da consulta do horário
op <- options(digits.secs = 2)

# Fazendo o calculo usando a função imap (equivale a usar o plano "sequential")
plan(sequential)
tic()
imap(time_sleep, ~ func(.x, .y))
toc()

# Paralelizando nos cores da máquina local
plan(multisession, workers = 6)
tic()
future_imap(time_sleep, ~ func(.x, .y))
toc()

# Paralelizando nos cores de uma única máquina virtual
#plan(cluster, workers = as.cluster(vm))
plan(cluster, workers = cl)
tic()
future_map(.x = list(node1 = time_sleep), 
           .f = ~ {
             plan(multisession, workers = 6)
             future_imap(
               .x = .x,
               .f = ~ func(.x, .y)
             )
           }, 
           .options = furrr_options(seed=42)
)
toc()

#### Time series
library(forecast)
library(Mcomp)
files = c('ind_month', 'ind_quart', 'ind_year', 'ind_other')
r = lapply(files, readRDS)
names(r) = files
for (i in 1:length(r)){
  assign(names(r)[i], r[[i]])
}
rm(list = c('files', 'r', 'i'))
n = length(M3)

prep_auto = function(ts, indice) { # iteração j e lista M formada por ts's
  
  print(str_c("Replicação ", indice, ": ", Sys.time()))
  mod = auto.arima(ts) 
  
  return(mod)
}


# Fazendo o calculo usando a função imap (equivale a usar o plano "sequential")
M3_list = list()
for (i in 1:100) {
  M3_list[[i]] = M3[[i + 1400]]$x
}

plan(sequential)
tic()
imap(M3_list, ~ prep_auto(.x, .y))
toc()

plan(cluster, workers = cl)
tic()
future_map(.x = list(node1 = M3_list), 
           .f = ~ {
             plan(multisession, workers = 3)
             future_imap(
               .x = .x,
               .f = ~ prep_auto(.x, .y)
             )
           }, 
           .options = furrr_options(seed=42)
)
toc()

theta_hat = cor(law$LSAT, law$GPA)
B = 500
theta_b = numeric()
n=nrow(law)

law_list = rep(list(law), 10000)

boot_function = function(law_data, indice){
  print(str_c("Replicação ", indice, ": ", Sys.time()))
  i = sample(1:n, n, replace = TRUE)
  theta_b[b] = cor(law_data$LSAT[i], law_data$GPA[i])
}

plan(sequential)
tic()
imap(law_list, ~ boot_function(.x, .y))
toc()

vies = mean(theta_b) - theta_hat

se = sd(theta_b)

plan(cluster, workers = cl)
tic()
future_map(.x = list(node1 = law_list), 
           .f = ~ {
             plan(multisession, workers = 2)
             theta_b = numeric()
             n=nrow(law)
             future_imap(
               .x = .x,
               .f = ~ boot_function(.x, .y)
             )
           }, 
           .options = furrr_options(seed=42)
)
toc()




