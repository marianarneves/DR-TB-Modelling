library(dplyr)
library(tidyr)
library(stringr)

# ----------------------------
# Prepare data
# ----------------------------
x <- as.data.frame(x)

x <- x %>%
  mutate(
    Age_bin = cut(Age,
                  breaks = seq(0, 100, by = 20),
                  right = FALSE,
                  include.lowest = TRUE),
    Family_size_bin = cut(Family_size,
                          breaks = seq(0, 12, by = 4),
                          right = FALSE,
                          include.lowest = TRUE),
    Family_size18_bin = cut(
      Family_size18,
      breaks = c(0, 2, 12),   # 0–2 and 2–12
      right = TRUE,           # intervals are right-closed (a, b]
      include.lowest = TRUE   # include 0 in the first interval
    )
  )


dummy_exclude <- c(
  "Age", "Family_size", "Family_size18",
  "Age_bin", "Family_size_bin", "Family_size18_bin"
)

# ----------------------------
# Dummy variables: counts + reference
# ----------------------------
dummy_weights <- x %>%
  pivot_longer(
    cols = -all_of(dummy_exclude),
    names_to = "column",
    values_to = "value"
  ) %>%
  mutate(
    variable = str_remove(column, "_[^_]+$"),
    category = str_remove(column, "^.*_")
  ) %>%
  group_by(variable, category) %>%
  summarise(n = sum(value), .groups = "drop") %>%
  bind_rows(
    x %>%
      pivot_longer(
        cols = -all_of(dummy_exclude),
        names_to = "column",
        values_to = "value"
      ) %>%
      mutate(variable = str_remove(column, "_[^_]+$")) %>%
      distinct(variable, column) %>%
      group_by(variable) %>%
      summarise(
        n = sum(rowSums(x[, column, drop = FALSE]) == 0),
        category = "ref",
        .groups = "drop"
      )
  ) %>%
  group_by(variable) %>%
  mutate(weight = n / sum(n)) %>%
  ungroup()

# ----------------------------
# Binned variables
# ----------------------------
bin_weights <- bind_rows(
  x %>%
    count(Age_bin, name = "n") %>%
    mutate(variable = "Age", category = as.character(Age_bin)),
  x %>%
    count(Family_size_bin, name = "n") %>%
    mutate(variable = "Family_size", category = as.character(Family_size_bin)),
  x %>%
    count(Family_size18_bin, name = "n") %>%
    mutate(variable = "Family_size18", category = as.character(Family_size18_bin))
) %>%
  group_by(variable) %>%
  mutate(weight = n / sum(n)) %>%
  ungroup() %>%
  select(variable, category, n, weight)

# ----------------------------
# Final result
# ----------------------------
feature_weights <- bind_rows(dummy_weights, bin_weights) %>%
  group_by(variable) %>%
  mutate(weight = weight / sum(weight)) %>%
  ungroup() %>%
  arrange(variable, category)
