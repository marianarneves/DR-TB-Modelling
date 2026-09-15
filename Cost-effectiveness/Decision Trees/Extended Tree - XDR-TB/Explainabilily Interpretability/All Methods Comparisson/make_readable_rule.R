make_human_rule <- function(description, dict) {
  
  # Helper: apply dictionary replacement to any variable name
  replace_with_dict <- function(text, dict) {
    for (v in names(dict)) {
      text <- gsub(paste0("\\b", v, "\\b"), dict[[v]], text)
    }
    text
  }
  
  # Helper: process one variable interval like "0 <= X <= 0"
  process_single_variable <- function(desc) {
    # Extract variable name
    var <- sub(".*<=\\s*([A-Za-z0-9_]+)\\s*<=.*", "\\1", desc)
    
    # Extract numeric limits
    nums <- as.numeric(unlist(regmatches(desc, gregexpr("[0-9]+", desc))))
    lower <- nums[1]
    upper <- nums[2]
    
    # CASE A: both limits equal
    if (lower == upper) {
      if (lower == 0) {
        # No variable
        return(paste("No", var))
      } else if (lower == 1) {
        # Just variable name
        return(var)
      }
    }
    
    # CASE B: interval with different limits → keep only variable
    return(var)
  }
  
  # Helper: process a multi-variable rule
  process_multi_rule <- function(desc) {
    parts <- strsplit(desc, "&")[[1]]
    parts <- trimws(parts)
    
    processed_parts <- sapply(parts, function(p) {
      # Extract var
      var <- sub("(.*?)(<=|>=|>|<).*", "\\1", p)
      var <- trimws(var)
      
      # Extract sign
      sign <- sub(".*?(<=|>=|>|<).*", "\\1", p)
      
      # Extract number
      num <- as.numeric(gsub(".*?(<=|>=|>|<)\\s*([0-9]+).*", "\\2", p))
      
      # Logic
      if (sign == "<=" && num == 0) {
        paste("No", var)
      } else if (sign %in% c(">=", ">", "<") || (sign == "<=" && num > 0)) {
        var  # Keep plain variable name
      } else {
        var
      }
    })
    
    paste(processed_parts, collapse = " AND ")
  }
  
  # Detect if rule or single variable
  is_rule <- grepl("&", description)
  
  if (is_rule) {
    out <- process_multi_rule(description)
  } else {
    out <- process_single_variable(description)
  }
  
  # Apply dictionary replacement at the end
  out <- replace_with_dict(out, dict)
  
  return(out)
}
