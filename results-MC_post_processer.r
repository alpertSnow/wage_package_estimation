library(tidyverse)
library(data.table)
library(hrbrthemes)
library(scales)
library(ggridges)

# settings
windowsFonts(cnfont = windowsFont("微软雅黑")) #思源宋体 CN
theme_set(theme_grey(base_family = "cnfont"))

# define functions
## 计算各单位两个分位数和均值
quantile.cal <- function(df, var, asPercent=FALSE, q1=0.025, q2=0.975){
    q1.name <- paste(var, q1, sep = "_")
    mean.name <- paste(var, "mean", sep = "_")
    q2.name <- paste(var, q2, sep = "_")
    q1 <- df %>% summarise_at(var, ~ quantile(., q1, na.rm=TRUE)) %>% rename(q1=var)
    mean <- df %>% summarise_at(var, ~ mean(., na.rm=TRUE)) %>% rename(mean=var)
    q2 <- df %>% summarise_at(var, ~ quantile(., q2, na.rm=TRUE)) %>% rename(q2=var)
    output <- q1 %>% full_join(mean, by="name") %>% full_join(q2, by="name")
    if (asPercent==TRUE){
        output$q1 <- percent(output$q1, accuracy = 0.01)
        output$mean <- percent(output$mean, accuracy = 0.01)
        output$q2 <- percent(output$q2, accuracy = 0.01)
    }
    colnames(output)[2] <- q1.name
    colnames(output)[3] <- mean.name
    colnames(output)[4] <- q2.name
    output
}

# 读取数据，排序
db.zhuangbei <- fread("results-zhuangbei-MC.csv", encoding = "UTF-8") %>% 
    filter(subcategory=="")
db <- fread("results-MC.csv", encoding = "UTF-8") %>% 
    bind_rows(db.zhuangbei) %>%
    mutate(package_change=package_real - package_last_year) %>% 
    mutate(avg_wage_change=avg_wage_real - avg_wage_last_year)
var_names <- c("compete_approved", "fazhan", "keji", "zulin", "zixun", "compete_section", 
               "zhuangbei",
               "special_approved","guidao", "luwang", "zichan", "guanlang", 
               "jiaotong", "tudi", "duojing", "beixin", "dahebing", "kegongsi", 
               "dahebing_minus", "jiguan_plus", "special_elimination", "special_section", 
               "public_approved", "yunying", "public_elimination", "public_section")
db$var_name <- factor(db$var_name, levels = var_names)
db <- arrange(db, var_name) %>% group_by(name)
db$name <- factor(db$name, levels = unique(db$name))
db[db$var_name=="dahebing",]$name = "机关本部"

# 摘出来各版块
compete_units <- c("compete_approved", "fazhan", "keji", "zulin", "zixun", 
                   "compete_section", "zhuangbei")
compete_units_db <- db %>% filter(var_name %in% compete_units)
special_units <- c("special_approved", "guidao", "luwang", "zichan", "guanlang", 
                   "jiaotong", "tudi", "duojing", "beixin", "dahebing", "special_section")
special_units_db <- db %>% filter(var_name %in% special_units)
c_s_units <- c("compete_approved", "fazhan", "keji", "zulin", "zixun", "compete_section", "zhuangbei",
                   "special_approved", "guidao", "luwang", "zichan", "guanlang", 
                   "jiaotong", "tudi", "duojing", "beixin", "dahebing", "special_section")
c_s_units_db <- db %>% filter(var_name %in% c_s_units)

# 数据总结
## 竞争与特殊版块
c_s.rate_3 <- quantile.cal(c_s_units_db, "rate_3", TRUE)  # 绩效联动增幅
c_s.package_3 <- quantile.cal(c_s_units_db, "package_3")  # 绩效联动工资部分
c_s.package_real <- quantile.cal(c_s_units_db, "package_real")  # 工资总额（含上年递延）
c_s.package_change <- quantile.cal(c_s_units_db, "package_change")  # 工资总额绝对值变化
c_s.deduct_final <- quantile.cal(c_s_units_db, "deduct_final")  # 年末统筹余额
c_s.avg_wage_real <- quantile.cal(c_s_units_db, "avg_wage_real")  # 人均工资
c_s.avg_wage_change <- quantile.cal(c_s_units_db, "avg_wage_change")  # 人均工资绝对值变化

c_s.quantiles <- c_s.rate_3 %>%  #合并表
    full_join(c_s.package_3, by = "name") %>%
    full_join(c_s.package_real, by = "name") %>%
    full_join(c_s.package_change, by = "name") %>%
    full_join(c_s.deduct_final, by = "name") %>%
    full_join(c_s.avg_wage_real, by = "name") %>%
    full_join(c_s.avg_wage_change, by = "name") 

## possibility to tune
section <- "compete_section"
tune_alpha <- db %>% filter(var_name==section) %>% pull(tune_alpha)
p.tune_alpha <- 1 - sum(tune_alpha==1)/length(tune_alpha)
tune_beta <- db %>% filter(var_name==section) %>% pull(tune_beta)
p.tune_beta <- 1 - sum(tune_beta==1)/length(tune_beta)

# 输出
write.csv(c_s.quantiles, "compete_special_quantiles.csv", row.names = FALSE)

# 作图
## 分位数图
quantiles_95 <- function(x) {
    r <- quantile(x, probs=c(0.025, 0.25, 0.5, 0.75, 0.975))
    names(r) <- c("ymin", "lower", "middle", "upper", "ymax")
    r
}

g1 <- ggplot(special_units_db, aes(x=name, y=rate_real)) +
    guides(fill=F) +
    stat_summary(fun.data = quantiles_95, geom="boxplot") +
    xlab("") +
    theme_bw()
plot(g1)

## 分布图
### 特殊功能板块总额增幅
g2 <- ggplot(special_units_db %>% filter(var_name!="special_approved"), 
    aes(x = rate_real, y = name, fill = stat(x))) +
    geom_density_ridges_gradient(scale = 1, size = 0.3, rel_min_height = 0.01) +
    scale_fill_viridis_c(name = "总额增幅", option = "C") +
    labs(title = '特殊功能板块2021工资总额增幅') +
    xlab("工资总额增幅") + ylab("") +
    scale_x_continuous(limits = c(0,0.06), breaks = seq(0,0.06,0.01),
                       labels = percent(seq(0,0.06,0.01), accuracy = 1))
plot(g2)

### 竞争类板块联动总额增幅
g3 <- ggplot(compete_units_db %>% filter(var_name!="compete_approved"), 
             aes(x = rate_3, y = name, fill = stat(x))) +
    geom_density_ridges_gradient(scale = 1, size = 0.1, rel_min_height = 0.01) +
    scale_fill_viridis_c(name = "总额增幅", option = "C") +
    labs(title = '竞争类板块2021工资总额增幅') +
    xlab("经济效益工资总额增幅") + ylab("") +
    scale_x_continuous(limits = c(-0.8,0.25), breaks = seq(-0.8,0.2,0.1),
                       labels = percent(seq(-0.8,0.2,0.1), accuracy = 1))
plot(g3)

