import uuid


class BaseMessage:
    """
    Represents a message in the network.
    Each message now has a unique ID.
    """

    id: str
    """
    The unique identifier of this message instance
    """

    content: str
    """
    The content of the message
    """

    creator_id: str
    """
    The ID of the creator of the message. Typically the ID of the node that created this message
    """

    def __init__(self, content: str, creator_id: str):
        self.id = uuid.uuid4().hex
        self.content = content
        self.creator_id = creator_id

    def __repr__(self):
        return f"Message(id={self.id}, content={self.content}, creator_id={self.creator_id})"
