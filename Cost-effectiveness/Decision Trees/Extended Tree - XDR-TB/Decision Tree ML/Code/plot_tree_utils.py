# === modeling/plot_tree_utils.py ===
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree, _tree

def save_sklearn_tree(clf, feature_names, output_path):
    plt.figure(figsize=(15, 10))
    plot_tree(clf, feature_names=feature_names, class_names=["BPaLC", "BPaLM"], filled=True,
              rounded=True, impurity=False, proportion=False, label='none', fontsize=100)
    plt.savefig(output_path, dpi=600)
    plt.close()

def draw_node(ax, text, xy, parent_xy=None):
    ax.text(xy[0], xy[1], text, ha='center', va='center',
            bbox=dict(boxstyle="round,pad=0.4", fc="lightblue", ec="black", lw=1.5))
    if parent_xy is not None:
        ax.plot([parent_xy[0], xy[0]], [parent_xy[1], xy[1]], 'k-')

def traverse_and_draw(ax, tree, node_id, depth, x=0.5, dx=0.25, y=1.0, dy=0.15, feature_names=None, class_names=None, parent_xy=None):
    if tree.feature[node_id] != _tree.TREE_UNDEFINED:
        name = feature_names[tree.feature[node_id]]
        draw_node(ax, name, (x, y), parent_xy)
        left_id = tree.children_left[node_id]
        x_left = x - dx / (depth + 1)
        y_child = y - dy
        traverse_and_draw(ax, tree, left_id, depth + 1, x_left, dx, y_child, dy, feature_names, class_names, (x, y))
        ax.text((x + x_left) / 2 - 0.03, (y + y_child) / 2 - 0.02, "No", fontsize=9, ha='center')

        right_id = tree.children_right[node_id]
        x_right = x + dx / (depth + 1)
        traverse_and_draw(ax, tree, right_id, depth + 1, x_right, dx, y_child, dy, feature_names, class_names, (x, y))
        ax.text((x + x_right) / 2 + 0.03, (y + y_child) / 2 - 0.02, "Yes", fontsize=9, ha='center')
    else:
        class_id = tree.value[node_id][0].argmax()
        draw_node(ax, class_names[class_id], (x, y), parent_xy)

def plot_custom_tree(clf, feature_names, class_names, output_path):
    fig, ax = plt.subplots(figsize=(15, 10))
    ax.axis('off')
    traverse_and_draw(ax, clf.tree_, 0, 0, feature_names=feature_names, class_names=class_names)
    plt.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close()

