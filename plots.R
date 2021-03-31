library(tidyverse)
library(data.table)
library(hrbrthemes)
library(ggridges)
library(plotly)

windowsFonts(cnfont = windowsFont("微软雅黑")) #思源宋体 CN
theme_set(theme_grey(base_family = "cnfont"))

db <- fread("results-1000.csv", encoding = "UTF-8")
db$var_name <- factor(db$var_name, levels = unique(db$var_name))
db <- db %>% group_by(var_name)
db_units <- db %>% filter(subcategory != "section" && subcategory != "approved")
db_section <- db %>% filter(subcategory == "section")
db_approved <- db %>% filter(subcategory == "approved")

results_names <- fread("results_chs_index.csv", encoding = "UTF-8", header = FALSE)
# su <- summarise(db, max = max(package_final), min = min(package_final))
units_names <- unique(db_units$name)
col_names <- colnames(select_if(db, is.numeric))
i <- "工资总额基础增幅"
var_to_show <- results_names %>% filter(V2 == i) %>% pull(1)

g1 <- ggplot(data = db_units, aes(x = avg_wage_final)) +
    geom_density(aes(fill = name), alpha = 0.5) + #facet_grid(cols = vars(name)) +
    labs(
        x = "Fuel efficiency (mpg)", y = "Weight (tons)",
        title = "示意图表"
        # subtitle = "A plot that is only useful for demonstration purposes",
        # caption = "Brought to you by the letter 'g'"
    )

g2 <- ggplot(data = db_units,  aes(x = avg_wage_final, y = name)) +
    stat_density_ridges(
        geom = "density_ridges_gradient",
        quantile_lines = TRUE, quantiles = c(0.025, 0.975)
    )
gg1 <- ggplotly(g1)
plot(g1)
# print(gg1)

# db1 <- db %>% filter(category == "Compete" && subcategory == "section")
su <- summary(db)
