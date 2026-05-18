plot_decision_tree <- function(tree_path) {
  # Load required packages.
  # - data.tree: convenient in-memory tree structure (Node objects).
  # - DiagrammeR: converts a data.tree into a graph and renders it.
  library(data.tree)
  library(DiagrammeR)
  
  # --- Read and parse file ---
  # Read the whole file into a character vector; each element is one line of the file.
  # 'tree_path' should be a string path to the file, e.g. "/Users/me/trees/mytree.txt".
  lines <- readLines(tree_path)
  
  # --- Helper function to count indentation depth ---
  # This inspects a single line and counts occurrences of the pattern "|   "
  # which is the indentation marker in the textual tree you provided.
  # The returned number is used to determine how deep that node is in the hierarchy.
  get_depth <- function(line) {
    matches <- gregexpr("\\|   ", line)[[1]]
    if (matches[1] == -1) return(0)  # no indentation markers -> depth 0 (top-level)
    length(matches)                   # number of matches = depth
  }
  
  # --- Replace threshold rules ---
  # Simplify decision-test text for nodes:
  # replace occurrences of the exact string "<= 0.50" with "No" and
  # occurrences of ">  0.50" with "Yes".
  # This is optional and depends on how you want thresholds labelled in the plot.
  lines <- gsub("<= 0.50", "No", lines)
  lines <- gsub(">  0.50", "Yes", lines)
  
  # --- Replace leaf classes with FQ / CFZ ---
  # Replace textual leaf labels "class: 0"/"class: 1" with short class tags "FQ"/"CFZ".
  # This makes leaf node labels compact and (in your domain) more meaningful.
  lines <- gsub("class: 0", "BPaLM", lines)
  lines <- gsub("class: 1", "BPaLC", lines)
  
  # --- Container for nodes at each depth ---
  # This list holds the most recently created node at each depth level.
  # We use it to attach new nodes to the correct parent as we scan the file.
  nodes_at_depth <- list()
  
  # --- Create artificial root node ---
  # We create a root container to which top-level nodes are attached.
  # If the file actually represents a single tree root, we'll remove this wrapper later.
  root <- Node$new("Root")
  
  # --- Parse lines into a data.tree structure ---
  for (line in lines) {
    # Skip blank/empty lines in the file.
    if (trimws(line) == "") next
    
    # Determine indentation depth for this line (0 = top-level).
    depth <- get_depth(line)
    
    # Clean node label:
    # Remove leading indentation and the typical "|--- " branch marker so the label is tidy.
    # The regex: ^\\|?( *\\|   )*\\|--- ? removes optional leading "|" and repeated " |   " blocks
    # followed by the "|--- " that appears in many ASCII tree dumps.
    label <- sub("^\\|?( *\\|   )*\\|--- ?", "", line)
    label <- trimws(label)            # remove remaining leading/trailing whitespace
    if (label == "") next             # if nothing remains after cleaning, skip the line
    
    # Create a new data.tree node with the cleaned label.
    new_node <- Node$new(label)
    
    if (depth == 0) {
      # Depth 0 nodes are attached directly to our artificial root.
      root$AddChildNode(new_node)
      # Store the most recent node at depth 0 (for linking future children).
      nodes_at_depth[[1]] <- new_node
    } else {
      # For deeper nodes, find the nearest existing parent by walking up depths.
      # parent_depth starts at the current depth and decreases until we find an existing node.
      parent_depth <- depth
      while (is.null(nodes_at_depth[[parent_depth]]) && parent_depth > 0) {
        parent_depth <- parent_depth - 1
      }
      # After the loop, parent_depth refers to the nearest ancestor that exists.
      parent_node <- nodes_at_depth[[parent_depth]]
      # Attach the new node as a child of that parent.
      parent_node$AddChildNode(new_node)
      # Record the new node as the most recent node at its depth+1 (children will attach here).
      nodes_at_depth[[depth + 1]] <- new_node
    }
  }
  
  # --- Remove artificial root if only one real child ---
  # If the artificial root has exactly one child, that child is the actual tree root
  # and we prefer to work with it directly (so the rendered graph doesn't show "Root").
  if (length(root$children) == 1) {
    tree <- root$children[[1]]
  } else {
    tree <- root
  }
  
  # --- Style nodes ---
  # Set a simple style attribute for all nodes in the tree. This is passed into
  # the DiagrammeR conversion and influences box shape and fill color.
  tree$Set(style = "filled, rounded", fillcolor = "lightblue")
  
  # --- Convert to DiagrammeR and plot ---
  # ToDiagrammeRGraph converts the data.tree object into a DiagrammeR (graphviz) graph.
  # DiagrammeR::render_graph() renders that graph to the RStudio Viewer or browser.
  graph <- ToDiagrammeRGraph(tree)
  return(graph)
}
