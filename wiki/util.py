import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

ENTRIES_PATH = 'entries'

def get_filename(title):
    return f"{ENTRIES_PATH}/{title}.md"


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir(ENTRIES_PATH)
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    delete_entry(title)
    default_storage.save(get_filename(title), ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(get_filename(title))
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None

def entry_exists(title):
    return default_storage.exists(get_filename(title))

def delete_entry(title):
    filename = get_filename(title)
    if default_storage.exists(filename):
        default_storage.delete(filename)
        return True
    return False
