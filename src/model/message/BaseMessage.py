import time
import uuid
from typing import List

from model.setting.model_settings import (
    SupportedEntity,
    BaseModelSetting,
    StringSetting,
)


class BaseMessage:
    """
    Represents a message in the network.
    Each message now has a unique ID.
    """

    id: str
    """
    The unique identifier of this message instance
    """

    _content: str  # Private attribute for content

    original_content: str
    """
    The original content of the message. This will be preserved even if the message content is modified by nodes when they apply any processing or encryption etc.
    """

    size: int
    """
    The size of the message in bytes. This is directly extracted from the message content
    """

    creator_id: str
    """
    The ID of the creator of the message. Typically the ID of the node that created this message
    """

    created_time: float
    """
    The time at which the message was created
    """

    settings: List[BaseModelSetting] = [
        StringSetting(
            name="Original Content",
            description="The original content of the message. This will be preserved even if the message content is modified by nodes.",
            default_value="Demo Message",
            entity_type=SupportedEntity.MESSAGE,
            attributes=["original_content"],
        ),
    ]

    def __init__(self, original_content: str, creator_id: str):
        self.id = uuid.uuid4().hex
        self.original_content = original_content
        self._content = ""
        self.creator_id = creator_id
        self.created_time = time.time()
        self._update_size()

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value
        self._update_size()

    def _update_size(self):
        self.size = len(self._content.encode())

    def __repr__(self):
        return f"Message(id={self.id}, content={self.content}, original_content={self.original_content}, creator_id={self.creator_id}, size={self.size})"
