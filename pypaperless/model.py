from datetime import datetime
from typing import List

from .auth import Auth


class Correspondent:
    """Class that represents a Light object in the ExampleHub API."""

    def __init__(self, raw_data: dict, auth: Auth):
        """Initialize a light object."""
        self.raw_data = raw_data
        self.auth = auth

    @property
    def id(self) -> int:
        """Return the count."""
        return self.raw_data["id"]

    @property
    def slug(self) -> str:
        """Return the count."""
        return self.raw_data["slug"]

    @property
    def name(self) -> str:
        """Return the count."""
        return self.raw_data["name"]

    @property
    def match(self) -> str:
        """Return the count."""
        return self.raw_data["match"]

    @property
    def matching_algorithm(self) -> int:
        """Return the count."""
        return self.raw_data["matching_algorithm"]

    @property
    def is_insensitive(self) -> bool:
        """Return the count."""
        return self.raw_data["is_insensitive"]

    @property
    def document_count(self) -> int:
        """Return the count."""
        return self.raw_data["document_count"]

    @property
    def last_correspondence(self) -> datetime:
        """Return the count."""
        return self.raw_data["last_correspondence"]


class DocumentType:
    """Class that represents a Light object in the ExampleHub API."""

    def __init__(self, raw_data: dict, auth: Auth):
        """Initialize a light object."""
        self.raw_data = raw_data
        self.auth = auth

    @property
    def id(self) -> int:
        """Return the count."""
        return self.raw_data["id"]

    @property
    def slug(self) -> str:
        """Return the count."""
        return self.raw_data["slug"]

    @property
    def name(self) -> str:
        """Return the count."""
        return self.raw_data["name"]

    @property
    def match(self) -> str:
        """Return the count."""
        return self.raw_data["match"]

    @property
    def matching_algorithm(self) -> int:
        """Return the count."""
        return self.raw_data["matching_algorithm"]

    @property
    def is_insensitive(self) -> bool:
        """Return the count."""
        return self.raw_data["is_insensitive"]

    @property
    def document_count(self) -> int:
        """Return the count."""
        return self.raw_data["document_count"]


class Tag:
    """Class that represents a Light object in the ExampleHub API."""

    def __init__(self, raw_data: dict, auth: Auth):
        """Initialize a light object."""
        self.raw_data = raw_data
        self.auth = auth

    @property
    def id(self) -> int:
        """Return the count."""
        return self.raw_data["id"]

    @property
    def slug(self) -> str:
        """Return the count."""
        return self.raw_data["slug"]

    @property
    def name(self) -> str:
        """Return the count."""
        return self.raw_data["name"]

    @property
    def colour(self) -> int:
        """Return the colour."""
        return self.raw_data["colour"]

    @property
    def match(self) -> str:
        """Return the count."""
        return self.raw_data["match"]

    @property
    def matching_algorithm(self) -> int:
        """Return the count."""
        return self.raw_data["matching_algorithm"]

    @property
    def is_insensitive(self) -> bool:
        """Return the count."""
        return self.raw_data["is_insensitive"]

    @property
    def is_inbox_tag(self) -> bool:
        """Return the count."""
        return self.raw_data["is_inbox_tag"]

    @property
    def document_count(self) -> int:
        """Return the count."""
        return self.raw_data["document_count"]


class SavedView:
    """Class that represents a Light object in the ExampleHub API."""

    def __init__(self, raw_data: dict, auth: Auth):
        """Initialize a light object."""
        self.raw_data = raw_data
        self.auth = auth

    @property
    def id(self) -> int:
        """Return the count."""
        return self.raw_data["id"]

    @property
    def name(self) -> str:
        """Return the count."""
        return self.raw_data["name"]

    @property
    def show_on_dashboard(self) -> bool:
        """Return the count."""
        return self.raw_data["show_on_dashboard"]

    @property
    def show_in_sidebar(self) -> bool:
        """Return the count."""
        return self.raw_data["show_in_sidebar"]

    @property
    def sort_field(self) -> str:
        """Return the count."""
        return self.raw_data["sort_field"]

    @property
    def sort_reverse(self) -> bool:
        """Return the count."""
        return self.raw_data["sort_reverse"]

    @property
    def filter_rules(self) -> List[dict]:
        """Return the count."""
        return self.raw_data["filter_rules"]


class Document:
    """Class that represents a Light object in the ExampleHub API."""

    def __init__(self, raw_data: dict, auth: Auth):
        """Initialize a light object."""
        self.raw_data = raw_data
        self.auth = auth

    @property
    def id(self) -> int:
        """Return the count."""
        return self.raw_data["id"]

    @property
    def correspondent(self) -> int:
        """Return the count."""
        return self.raw_data["correspondent"]

    @property
    def document_type(self) -> int:
        """Return the count."""
        return self.raw_data["document_type"]

    @property
    def title(self) -> str:
        """Return the count."""
        return self.raw_data["title"]

    @property
    def content(self) -> str:
        """Return the count."""
        return self.raw_data["content"]

    @property
    def tags(self) -> List[int]:
        """Return the count."""
        return self.raw_data["tags"]

    @property
    def created(self) -> datetime:
        """Return the count."""
        return self.raw_data["created"]

    @property
    def modified(self) -> datetime:
        """Return the count."""
        return self.raw_data["modified"]

    @property
    def added(self) -> datetime:
        """Return the count."""
        return self.raw_data["added"]

    @property
    def archive_serial_number(self) -> str:
        """Return the count."""
        return self.raw_data["archive_serial_number"]

    @property
    def original_file_name(self) -> str:
        """Return the count."""
        return self.raw_data["original_file_name"]

    @property
    def archived_file_name(self) -> str:
        """Return the count."""
        return self.raw_data["archived_file_name"]
