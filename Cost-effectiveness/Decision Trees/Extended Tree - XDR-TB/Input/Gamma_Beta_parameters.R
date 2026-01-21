findBetaAlphaBeta = function(mu, sigma2){
  alpha = ((1-mu)/sigma2 - 1/mu) * mu^2
  beta = alpha * (1/mu - 1)
  
  par = data.frame(par = c("alpha", "beta"), val = c(round(alpha,3), round(beta,3)))
  
  return(par)
}

findGammaAlphaBeta = function(mu, sigma2){
  alpha = (mu^2)/(sigma2)
  beta = (mu)/(sigma2)
  
  par = data.frame(par = c("alpha", "beta"), val = c(round(alpha,3), round(beta,3)))
  
  return(par)
}

