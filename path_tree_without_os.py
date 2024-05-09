import subprocess


def create_path_tree(root_dir):
  """
  Creates a dictionary representing the path tree using bash commands.

  Args:
      root_dir: The root directory path (string).

  Returns:
      A dictionary representing the path tree with the same structure as the
      original version.

  Raises:
      RuntimeError: If there's an error running the bash commands.
  """

  tree = {}

  # List directory contents using `ls -l` (long format)
  try:
    output = subprocess.run(['bash', '-c', f'ls -l {root_dir}'], capture_output=True, text=True, check=True).stdout
  except subprocess.CalledProcessError as e:
    raise RuntimeError(f"Error listing directory: {e}")

  # Process each line in the output (excluding header)
  for line in output.splitlines()[1:]:
    # Split line by spaces, avoiding extra splits with quoted filenames
    parts = line.split(maxsplit=8)
    permissions = parts[0]
    # Extract filename (assuming last part or part before last if space exists)
    filename = parts[-1] if len(parts) > 1 and ' ' not in parts[-2] else parts[-2]

    # Check file type using `file` command (or `stat` if `file` not available)
    try:
      file_type = subprocess.run(['bash', '-c', f'file -b {root_dir}/{filename}'], capture_output=True, text=True, check=True).stdout.strip()
    except subprocess.CalledProcessError:
      # If `file` not available, use `stat` as a fallback (might not be as precise)
      file_type = subprocess.run(['bash', '-c', f'stat -c %F {root_dir}/{filename}'], capture_output=True, text=True, check=True).stdout.strip()

    if file_type.startswith('regular'):  # Regular file
      tree.setdefault(filename, []).append(filename)
    elif file_type.startswith('directory'):
      child_tree = create_path_tree(f"{root_dir}/{filename}")  # Build full path in string
      if child_tree:  # Add subtree only if it's not empty
        tree[filename] = {'files': [], 'children': child_tree}

  return tree


if __name__ == '__main__':
  root_path = '/path/to/your/directory'  # Replace with your root directory
  try:
    path_tree = create_path_tree(root_path)
    print(path_tree)
  except RuntimeError as e:
    print(f"Error creating path tree: {e}")
