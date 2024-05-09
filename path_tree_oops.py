import subprocess


class DirectoryTree:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.tree = self._build_tree(root_dir)

    def _build_tree(self, root_dir):
        """
        Builds a dictionary representing the directory tree using bash commands.

        Args:
            root_dir: The root directory path (string).

        Returns:
            A dictionary representing the directory tree with the following structure:
                {
                    'folder_name': {
                        'files': [list of filenames],
                        'children': {  # Dictionary for subfolders
                            'subfolder1_name': {...},
                            # ...
                        }
                    },
                    # ... other folders in root_dir
                }
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
                # If `file` not available, use `stat` as a fallback (might not be precise)
                file_type = subprocess.run(['bash', '-c', f'stat -c %F {root_dir}/{filename}'], capture_output=True, text=True, check=True).stdout.strip()

            if file_type.startswith('regular'):  # Regular file
                tree.setdefault(filename, []).append(filename)
            elif file_type.startswith('directory'):
                child_tree = DirectoryTree(f"{root_dir}/{filename}")  # Create sub-tree object
                tree[filename] = {'files': child_tree.get_files(), 'children': child_tree.get_children()}

        return tree

    def get_files(self):
        """
        Returns a list of all files in the tree (including subdirectories).
        """

        all_files = []
        if 'files' in self.tree:
            all_files.extend(self.tree['files'])
        for child in self.tree.get('children', {}).values():
            all_files.extend(child.get_files())
        return all_files

    def get_children(self):
        """
        Returns a dictionary of subdirectories in the tree.
        """

        return self.tree.get('children', {})

    def __str__(self):
        """
        Returns a string representation of the directory tree with indentation.
        """

        def _format_tree(tree, level=0):
            lines = []
            indent = '  ' * level
            for name, data in tree.items():
                lines.append(f"{indent}{name}/")
                if 'files' in data:
                    lines.extend([f"{indent}  - {file}" for file in data['files']])
                if 'children' in data:
                    lines.extend(_format_tree(data['children'], level + 1))
            return lines

        return '\n'.join(_format_tree(self.tree))


if __name__ == '__main__':
    root_path = '.'  # Replace with your root directory
    tree = DirectoryTree(root_path)
    print(tree)
