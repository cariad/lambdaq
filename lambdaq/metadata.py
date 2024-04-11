from boto3 import Session


class Metadata:
    """
    Message handling metadata.

    Arguments:
        session: Boto3 session.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session
        """
        Boto3 session.
        """
