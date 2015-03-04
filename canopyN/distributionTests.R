

y= rnorm(10, mean = 385, sd = 4.5)
x <- seq(1,10,by=1)
plot(x,y)


plot(function(x) y, -660, 560,main = "wer")

plot(function(x) rnorm(x, mean = 385, sd = 4.5), -60, 50,
     main = "wer")


plot(function(x) pnorm(x, log.p = TRUE), -50, 10,
     main = "log { Normal Cumulative }")



#AVIRIS
xseq<-seq(348,368,.01)
densities<- dnorm(xseq, 358,1)

plot(xseq, densities, col="darkgreen",xlab="", ylab="Density", type="l", main="PDF of Standard Normal")