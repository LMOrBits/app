def add_items_to_gitignore(items: list, gitignore_path: str):
    # read the gitignore file
    with open(gitignore_path, 'r') as file:
        lines = file.readlines()
    # add the items to the gitignore file if not already present
    for item in items:
        item_str = str(item)  # Convert item to string if it's not
        if item_str not in lines:
            lines.append(item_str + '\n')  # Ensure each item ends with a newline
    # write the updated gitignore file
    with open(gitignore_path, 'w') as file:
        file.writelines(lines)
