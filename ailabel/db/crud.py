from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime
from .models import Topic, Label, LabeledPayload
from .database import with_session


@with_session
def create_topic(session: Session, name: str) -> Topic:
    """Create a new topic."""
    topic = Topic(name=name)
    session.add(topic)
    session.commit()
    session.refresh(topic)
    return topic


@with_session
def create_label(session: Session, name: str, topic_name: str) -> Label:
    """Create a new label for a topic."""
    label = Label(name=name, topic_name=topic_name)
    session.add(label)
    session.commit()
    session.refresh(label)
    return label


@with_session
def create_labeled_payload(session: Session, payload: str, label_name: str, topic_name: str) -> LabeledPayload:
    """Store a labeled payload."""
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
def get_all_topics(session: Session) -> List[Topic]:
    """Get all topics."""
    statement = select(Topic)
    return session.exec(statement).all()


@with_session
def get_topic(session: Session, name: str) -> Optional[Topic]:
    """Get a specific topic by name."""
    statement = select(Topic).where(Topic.name == name)
    return session.exec(statement).first()


@with_session
def get_labels_for_topic(session: Session, topic_name: str) -> List[Label]:
    """Get all labels for a specific topic."""
    statement = select(Label).where(Label.topic_name == topic_name)
    return session.exec(statement).all()


@with_session
def get_label_statistics(session: Session, topic_name: str) -> dict[str, int]:
    """Get distribution statistics of labels for a given topic.

    Args:
        session (Session): The database session
        topic_name (str): Name of the topic to get statistics for

    Returns:
        dict[str, int]: Dictionary mapping label names to their count frequencies
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
    """Check if a topic exists."""
    statement = select(Topic).where(Topic.name == name)
    return session.exec(statement).first() is not None


@with_session
def get_recent_labeled_payloads(
    session: Session,
    topic_name: str,
    limit: int = 10,
) -> List[LabeledPayload]:
    """Get recent labeled payloads for a topic."""
    statement = (
        select(LabeledPayload)
        .where(LabeledPayload.topic_name == topic_name)
        .order_by(LabeledPayload.created_at.desc())
        .limit(limit)
    )
    return session.exec(statement).all()
