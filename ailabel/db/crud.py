"""CRUD operations for database models.

This module provides Create, Read, Update, and Delete operations for the database models.
All functions use the `with_session` decorator to handle database sessions automatically.

The module includes operations for:
- Creating and retrieving topics
- Creating and retrieving labels
- Creating and retrieving labeled payloads
- Getting statistics and checking existence of data
"""

from typing import Optional
from sqlmodel import Session, select
from .models import Topic, Label, LabeledPayload
from .database import with_session


@with_session
def create_topic(session: Session, name: str) -> Topic:
    """Create a new topic.

    Args:
        session: The database session
        name: The name of the topic to create

    Returns:
        The created Topic object

    Raises:
        IntegrityError: If a topic with the same name already exists
    """
    topic = Topic(name=name)
    session.add(topic)
    session.commit()
    session.refresh(topic)
    return topic


@with_session
def create_label(session: Session, name: str, topic_name: str) -> Label:
    """Create a new label for a topic.

    Args:
        session: The database session
        name: The name of the label to create
        topic_name: The name of the topic this label belongs to

    Returns:
        The created Label object

    Raises:
        IntegrityError: If a label with the same name already exists or the topic doesn't exist
    """
    label = Label(name=name, topic_name=topic_name)
    session.add(label)
    session.commit()
    session.refresh(label)
    return label


@with_session
def create_labeled_payload(session: Session, payload: str, label_name: str, topic_name: str) -> LabeledPayload:
    """Store a labeled payload.

    Args:
        session: The database session
        payload: The text content to label
        label_name: The name of the label to apply
        topic_name: The name of the topic this labeled payload belongs to

    Returns:
        The created LabeledPayload object

    Raises:
        IntegrityError: If the label or topic doesn't exist
    """
    labeled_payload = LabeledPayload(
        payload=payload,
        label_name=label_name,
        topic_name=topic_name,
    )
    session.add(labeled_payload)
    session.commit()
    session.refresh(labeled_payload)
    return labeled_payload


@with_session
def get_all_topics(session: Session) -> list[Topic]:
    """Get all topics.

    Args:
        session: The database session

    Returns:
        A list of all Topic objects in the database
    """
    statement = select(Topic)
    return session.exec(statement).all()


@with_session
def get_topic(session: Session, name: str) -> Optional[Topic]:
    """Get a specific topic by name.

    Args:
        session: The database session
        name: The name of the topic to retrieve

    Returns:
        The Topic object if found, None otherwise
    """
    statement = select(Topic).where(Topic.name == name)
    return session.exec(statement).first()


@with_session
def get_labels_for_topic(session: Session, topic_name: str) -> list[Label]:
    """Get all labels for a specific topic.

    Args:
        session: The database session
        topic_name: The name of the topic to get labels for

    Returns:
        A list of Label objects for the specified topic
    """
    statement = select(Label).where(Label.topic_name == topic_name)
    return session.exec(statement).all()


@with_session
def get_label_statistics(session: Session, topic_name: str) -> dict[str, int]:
    """Get distribution statistics of labels for a given topic.

    Args:
        session: The database session
        topic_name: Name of the topic to get statistics for

    Returns:
        Dictionary mapping label names to their count frequencies
        where keys are label names and values are the number of occurrences

    Example:
        >>> get_label_statistics(session, "sentiment")
        {'positive': 42, 'negative': 28, 'neutral': 30}
    """
    statement = select(LabeledPayload).where(LabeledPayload.topic_name == topic_name)
    payloads = session.exec(statement).all()

    stats = {}
    for payload in payloads:
        stats[payload.label_name] = stats.get(payload.label_name, 0) + 1

    return stats


@with_session
def topic_exists(session: Session, name: str) -> bool:
    """Check if a topic exists.

    Args:
        session: The database session
        name: The name of the topic to check

    Returns:
        True if the topic exists, False otherwise
    """
    statement = select(Topic).where(Topic.name == name)
    return session.exec(statement).first() is not None


@with_session
def get_recent_labeled_payloads(
    session: Session,
    topic_name: str,
    limit: int = 10,
) -> list[LabeledPayload]:
    """Get recent labeled payloads for a topic.

    Args:
        session: The database session
        topic_name: The name of the topic to get payloads for
        limit: Maximum number of payloads to return (default: 10)

    Returns:
        A list of LabeledPayload objects ordered by creation date (newest first)
    """
    statement = (
        select(LabeledPayload)
        .where(LabeledPayload.topic_name == topic_name)
        .order_by(LabeledPayload.created_at.desc())
        .limit(limit)
    )
    return session.exec(statement).all()
