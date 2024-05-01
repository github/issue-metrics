""" Helper functions for working with markdown files. """


def markdown_too_large_for_issue_body(file_path: str, max_char_count: int) -> bool:
    """
    Check if the markdown file is too large to fit into a github issue.

    Inputs:
    file_path: str - the path to the markdown file to check
    max_char_count: int - the maximum number of characters allowed in a github issue body

    Returns:
    bool - True if the file is too large, False otherwise

    """
    with open(file_path, "r", encoding="utf-8") as file:
        file_contents = file.read()
        return len(file_contents) > max_char_count


def split_markdown_file(file_path: str, max_char_count: int) -> None:
    """
    Split the markdown file into smaller files.

    Inputs:
    file_path: str - the path to the markdown file to split
    max_char_count: int - the maximum number of characters allowed before splitting markdown file

    """
    with open(file_path, "r", encoding="utf-8") as file:
        file_contents = file.read()
        contents_list = [
            file_contents[i : i + max_char_count]
            for i in range(0, len(file_contents), max_char_count)
        ]
        for i, content in enumerate(contents_list):
            with open(f"{file_path[:-3]}_{i}.md", "w", encoding="utf-8") as new_file:
                new_file.write(content)
