adaptive <- c(0.7167,0.7389,0.7000,0.7500,0.6944,0.7778,0.7833,0.7556,0.7444,0.7278)
mlp <- c(0.7611,0.7667,0.7333,0.7000,0.7111,0.7667,0.7611,0.7278,0.7778,0.7278)

wilcox.test(adaptive, mlp, paired=TRUE)

install.packages("effsize")
library(effsize)

VD.A(adaptive, mlp)