import uuid
from typing import List, Dict, Any

from model.setting.model_setting_mixin import ModelSettingMixin
from model.setting.model_settings import (
    SupportedEntity,
    BaseModelSetting,
    StringSetting,
)


class BaseMessage(ModelSettingMixin):
    """
    Represents a message in the network.
    Each message now has a unique ID.
    """

    name: str = "Base Message"

    id: str
    """
    The unique identifier of this message instance
    """

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

    created_time: int
    """
    The Simulation step at which the message was created
    """

    hops: int = 0
    """
    The number of hops the message has taken in the network
    """

    _props: Dict[str, Any] = {}

    _content: str

    entity_type = SupportedEntity.MESSAGE

    settings: List[BaseModelSetting] = [
        StringSetting(
            name="Original Content",
            description="The original content of the message. This will be preserved even if the message content is modified by nodes.",
            default_value="Demo Message",
            entity_type=SupportedEntity.MESSAGE,
            attributes=["original_content", "content"],
        ),
    ]

    def __init__(self, original_content: str, creator_id: str, created_time: int):
        super().__init__()
        self.id = uuid.uuid4().hex
        self.original_content = original_content
        self._content = original_content
        self.creator_id = creator_id
        self.created_time = created_time
        self._update_size()

    @property
    def content(self):
        """
        Stores the content of the message. The content stored here may not be the original message as each node may modify the content with stuff like encryption etc.
        :return:
        """
        return self._content

    @content.setter
    def content(self, value):
        self._content = value
        self._update_size()

    @property
    def props(self):
        """
        Additional Properties that can be added to the message based on each implementation. Note that these properties are not saved in message content
        however they will still count towards the size of the message. Only the values of the props are measured and not the keys. This is to simulate
        a header in a message, as the header structure is already know by the nodes, only data is sent.
        """
        return self._props

    @props.setter
    def props(self, value):
        self._props = value
        self._update_size()

    def duplicate(
        self,
        creator_id: str,
        step: int,
        copy_time: bool = False,
    ) -> "BaseMessage":
        """
        Creates and returns a new message instance that is a copy of the current message,
        except for message_id and creation_time which will be new.
        """

        if copy_time:
            new_message = BaseMessage(
                self.original_content, creator_id, self.created_time
            )
        else:
            new_message = BaseMessage(self.original_content, creator_id, step)
        return new_message

    def _update_size(self) -> None:
        """
        Internal Method used to update the size of the message based on the content and the props it contains

        :return: None
        """
        self.size = len(self._content.encode()) + sum(
            len(str(value).encode()) for value in self.props.values()
        )

    def __repr__(self):
        return f"Message(id={self.id}, content={self.content}, original_content={self.original_content}, creator_id={self.creator_id}, size={self.size})"

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "original_content": self.original_content,
            "size": self.size,
            "creator_id": self.creator_id,
            "created_time": self.created_time,
            "hops": self.hops,
            "props": self.props,
        }

    @classmethod
    def deserialize(cls, data: dict) -> "BaseMessage":
        message = BaseMessage(
            data["original_content"],
            data["creator_id"],
            data["created_time"],
        )
        message.id = data["id"]
        message.size = data["size"]
        message.hops = data["hops"]
        message.props = data["props"]
        return message
