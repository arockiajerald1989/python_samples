import os


def create_path_tree(root_dir):
  """
  Creates a dictionary representing the path tree of a directory,
  including a "files" list for each directory and its subdirectories.

  Args:
      root_dir: The root directory path (string).

  Returns:
      A dictionary representing the path tree with the following structure:
          {
              'directory1': {
                  'files': ['file1.txt', 'file2.jpg'],  # List of all files
                  'directory2': { ... },  # Subdirectory with its own tree
              },
              # ... other entries in the root directory
          }
  """

  tree = {}
  for item in os.listdir(root_dir):
    item_path = os.path.join(root_dir, item)
    if os.path.isfile(item_path):
      # Capture files directly in the root directory
      tree.setdefault(item, []).append(item_path)  # Append full path for files
    else:
      child_tree = create_path_tree(item_path)  # Recursively create subtree
      tree[item] = {'files': []}  # Initialize empty "files" list
      if child_tree:
        # Add full paths of files from subdirectory and its subdirectories
        for sub_item in child_tree.values():
          if isinstance(sub_item, list):  # Handle list of files from subdirectories
            tree[item]['files'].extend(sub_item)
          else:  # Recursively add files from sub-subdirectories
            tree[item]['files'].extend(get_all_files(sub_item))

      tree[item]['directory'] = child_tree  # Add subdirectory tree

  return tree


def get_all_files(sub_tree):
  """
  Helper function to extract all files recursively from a sub-tree.

  Args:
      sub_tree: A dictionary representing a subdirectory tree.

  Returns:
      A list of full file paths within the sub-tree and its subdirectories.
  """
  files = []
  for item, value in sub_tree.items():
    if isinstance(value, list):
      # Directly append file paths from subdirectory's 'files' list
      files.extend(value)
    else:
      # Recursively call for sub-subdirectories
      files.extend(get_all_files(value))
  return files


if __name__ == '__main__':
  root_path = '/path/to/your/directory'  # Replace with your root directory
  path_tree = create_path_tree(root_path)
  print(path_tree)
