from uuid import uuid4


class MockUser:
    """A mock user class for testing purposes."""

    def __init__(self, username, email, hashed_password, id=None):
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.id = id if id else uuid4()


class MockDocumentType:
    """A mock document type class for testing purposes."""

    def __init__(self, id=None, name="Mock Document Type") -> None:
        self.id = id if id else uuid4()
        self.name = name
