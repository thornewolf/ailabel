import pytest
from sqlmodel import Session, select
from datetime import datetime

from ailabel.db.models import Topic, Label, LabeledPayload
from ailabel.db.crud import (
    create_topic,
    create_label,
    create_labeled_payload,
    get_all_topics,
    get_topic,
    get_labels_for_topic,
    get_label_statistics,
    topic_exists,
    get_recent_labeled_payloads
)


def test_create_topic(session: Session, sample_topic):
    """Test creating a topic."""
    # Create a topic
    topic = create_topic(name=sample_topic, session=session)
    
    # Verify the topic was created
    assert topic.name == sample_topic
    
    # Verify we can retrieve it from the database
    db_topic = session.exec(select(Topic).where(Topic.name == sample_topic)).first()
    assert db_topic is not None
    assert db_topic.name == sample_topic


def test_create_label(session: Session, sample_topic, sample_label):
    """Test creating a label."""
    # Create a topic first
    create_topic(name=sample_topic, session=session)
    
    # Create a label
    label = create_label(name=sample_label, topic_name=sample_topic, session=session)
    
    # Verify the label was created
    assert label.name == sample_label
    assert label.topic_name == sample_topic
    
    # Verify we can retrieve it from the database
    db_label = session.exec(select(Label).where(Label.name == sample_label)).first()
    assert db_label is not None
    assert db_label.name == sample_label
    assert db_label.topic_name == sample_topic


def test_create_labeled_payload(session: Session, sample_topic, sample_label, sample_payload):
    """Test creating a labeled payload."""
    # Create a topic and label first
    create_topic(name=sample_topic, session=session)
    create_label(name=sample_label, topic_name=sample_topic, session=session)
    
    # Create a labeled payload
    payload = create_labeled_payload(
        payload=sample_payload,
        label_name=sample_label,
        topic_name=sample_topic,
        session=session
    )
    
    # Verify the payload was created
    assert payload.payload == sample_payload
    assert payload.label_name == sample_label
    assert payload.topic_name == sample_topic
    assert isinstance(payload.id, str)
    assert isinstance(payload.created_at, datetime)
    
    # Verify we can retrieve it from the database
    db_payload = session.exec(
        select(LabeledPayload).where(LabeledPayload.payload == sample_payload)
    ).first()
    assert db_payload is not None
    assert db_payload.payload == sample_payload
    assert db_payload.label_name == sample_label
    assert db_payload.topic_name == sample_topic


def test_get_all_topics(session: Session):
    """Test getting all topics."""
    # Create multiple topics
    create_topic(name="topic1", session=session)
    create_topic(name="topic2", session=session)
    create_topic(name="topic3", session=session)
    
    # Get all topics
    topics = get_all_topics(session=session)
    
    # Verify we got all topics
    assert len(topics) == 3
    topic_names = {topic.name for topic in topics}
    assert topic_names == {"topic1", "topic2", "topic3"}


def test_get_topic(session: Session, sample_topic):
    """Test getting a specific topic."""
    # Create a topic
    create_topic(name=sample_topic, session=session)
    
    # Get the topic
    topic = get_topic(name=sample_topic, session=session)
    
    # Verify we got the right topic
    assert topic is not None
    assert topic.name == sample_topic
    
    # Test getting a non-existent topic
    non_existent = get_topic(name="non_existent", session=session)
    assert non_existent is None


def test_get_labels_for_topic(session: Session, sample_topic):
    """Test getting labels for a topic."""
    # Create a topic
    create_topic(name=sample_topic, session=session)
    
    # Create multiple labels for the topic
    create_label(name="label1", topic_name=sample_topic, session=session)
    create_label(name="label2", topic_name=sample_topic, session=session)
    create_label(name="label3", topic_name=sample_topic, session=session)
    
    # Get labels for the topic
    labels = get_labels_for_topic(topic_name=sample_topic, session=session)
    
    # Verify we got all labels
    assert len(labels) == 3
    label_names = {label.name for label in labels}
    assert label_names == {"label1", "label2", "label3"}


def test_get_label_statistics(session: Session, sample_topic):
    """Test getting label statistics for a topic."""
    # Create a topic
    create_topic(name=sample_topic, session=session)
    
    # Create labels
    create_label(name="positive", topic_name=sample_topic, session=session)
    create_label(name="negative", topic_name=sample_topic, session=session)
    create_label(name="neutral", topic_name=sample_topic, session=session)
    
    # Create labeled payloads
    for i in range(5):
        create_labeled_payload(
            payload=f"Positive payload {i}",
            label_name="positive",
            topic_name=sample_topic,
            session=session
        )
    
    for i in range(3):
        create_labeled_payload(
            payload=f"Negative payload {i}",
            label_name="negative",
            topic_name=sample_topic,
            session=session
        )
    
    for i in range(2):
        create_labeled_payload(
            payload=f"Neutral payload {i}",
            label_name="neutral",
            topic_name=sample_topic,
            session=session
        )
    
    # Get label statistics
    stats = get_label_statistics(topic_name=sample_topic, session=session)
    
    # Verify statistics
    assert stats["positive"] == 5
    assert stats["negative"] == 3
    assert stats["neutral"] == 2
    assert sum(stats.values()) == 10


def test_topic_exists(session: Session, sample_topic):
    """Test checking if a topic exists."""
    # Create a topic
    create_topic(name=sample_topic, session=session)
    
    # Check if the topic exists
    assert topic_exists(name=sample_topic, session=session) is True
    assert topic_exists(name="non_existent", session=session) is False


def test_get_recent_labeled_payloads(session: Session, sample_topic):
    """Test getting recent labeled payloads."""
    # Create a topic
    create_topic(name=sample_topic, session=session)
    
    # Create labels
    create_label(name="label1", topic_name=sample_topic, session=session)
    
    # Create 15 labeled payloads
    for i in range(15):
        create_labeled_payload(
            payload=f"Payload {i}",
            label_name="label1",
            topic_name=sample_topic,
            session=session
        )
    
    # Get recent payloads with default limit
    payloads = get_recent_labeled_payloads(topic_name=sample_topic, session=session)
    assert len(payloads) == 10  # Default limit is 10
    
    # Verify payloads are in reverse chronological order (newest first)
    assert payloads[0].payload == "Payload 14"
    assert payloads[9].payload == "Payload 5"
    
    # Test with custom limit
    payloads = get_recent_labeled_payloads(topic_name=sample_topic, limit=5, session=session)
    assert len(payloads) == 5
    assert payloads[0].payload == "Payload 14"
    assert payloads[4].payload == "Payload 10"