library(data.tree)
library(collapsibleTree)

collapsibletree_fromrules <- function(file_path){
  # Read all lines from the file
  lines <- readLines(file_path)
  
  # Replace rules
  lines <- gsub("<= 0.50", "No", lines)
  lines <- gsub(">  0.50", "Yes", lines)
  
  # Function to calculate depth based on number of '|   ' blocks before '|---'
  get_depth <- function(line) {
    pos <- regexpr("\\|---", line)
    if (pos == -1) return(NA)  # No tree node in this line
    prefix <- substr(line, 1, pos - 1)
    matches <- gregexpr("\\|   ", prefix)[[1]]
    if (matches[1] == -1) return(0)  # Root node has 0 blocks
    length(matches)
  }
  
  # Function to clean the node label (remove everything before '|---' and trim)
  clean_label <- function(line) {
    sub("^.*\\|--- ?", "", line) |> trimws()
  }
  
  # Create an artificial root node to hold all roots in your file
  root <- Node$new("Root")
  
  # Keep track of last node at each depth level, initialize depth 0 to root
  nodes_at_depth <- list()
  nodes_at_depth[[1]] <- root  # depth 0 corresponds to index 1 in this list
  
  # Parse each line and build the tree
  for (i in seq_along(lines)) {
    line <- lines[i]
    # Skip empty lines
    if (nchar(trimws(line)) == 0) next
    
    depth <- get_depth(line)
    if (is.na(depth)) next  # skip lines without node info
    
    label <- clean_label(line)
    new_node <- Node$new(label)
    
    # The parent is the node at one level above current depth
    # Because R lists are 1-based, parent is at nodes_at_depth[[depth]]
    parent <- nodes_at_depth[[depth + 1]]  # +1 because depth 0 is index 1
    if (is.null(parent)) {
      stop(sprintf("No parent node found for node '%s' at line %d with depth %d", label, i, depth))
    }
    
    parent$AddChildNode(new_node)
    
    # Update the last node at this depth + 1 (for future children)
    nodes_at_depth[[depth + 2]] <- new_node
  }
  
  # Optional: print the tree structure in console for verification
  # print(root, "name")
  
  # Prepare data.frame for collapsibleTree visualization
  paths <- root$Get("pathString")
  split_paths <- strsplit(paths, "/")
  max_levels <- max(sapply(split_paths, length))
  # Fill missing levels with NA
  paths_df <- do.call(rbind, lapply(split_paths, function(p) {
    length(p) <- max_levels
    p
  }))
  paths_df <- as.data.frame(paths_df, stringsAsFactors = FALSE)
  colnames(paths_df) <- paste0("Level", seq_len(ncol(paths_df)))
  
  # # Plot interactive collapsible tree
  collapsibleTree(
    paths_df,
    hierarchy = colnames(paths_df),
    root = "DT",
    fill = "lightblue",
    fontSize = 12,
    zoomable = TRUE
  )
  
}


