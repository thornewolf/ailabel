import pytest
from sqlmodel import Session
from datetime import datetime

from ailabel.db.models import Topic, Label, LabeledPayload


def test_topic_model(session: Session):
    """Test creating and retrieving a Topic."""
    # Create a topic
    topic_name = "test_topic"
    topic = Topic(name=topic_name)
    session.add(topic)
    session.commit()
    
    # Retrieve the topic
    session.refresh(topic)
    assert topic.name == topic_name
    assert isinstance(topic.labels, list)
    assert isinstance(topic.examples, list)
    assert len(topic.labels) == 0
    assert len(topic.examples) == 0


def test_label_model(session: Session):
    """Test creating and retrieving a Label with Topic relationship."""
    # Create a topic first
    topic_name = "test_topic"
    topic = Topic(name=topic_name)
    session.add(topic)
    session.commit()
    
    # Create a label for the topic
    label_name = "test_label"
    label = Label(name=label_name, topic_name=topic_name)
    session.add(label)
    session.commit()
    
    # Retrieve the label
    session.refresh(label)
    assert label.name == label_name
    assert label.topic_name == topic_name
    assert label.topic.name == topic_name
    assert isinstance(label.examples, list)
    assert len(label.examples) == 0


def test_labeled_payload_model(session: Session):
    """Test creating and retrieving a LabeledPayload with relationships."""
    # Create a topic
    topic_name = "test_topic"
    topic = Topic(name=topic_name)
    session.add(topic)
    
    # Create a label
    label_name = "test_label"
    label = Label(name=label_name, topic_name=topic_name)
    session.add(label)
    session.commit()
    
    # Create a labeled payload
    payload_text = "This is a test payload"
    labeled_payload = LabeledPayload(
        payload=payload_text,
        label_name=label_name,
        topic_name=topic_name
    )
    session.add(labeled_payload)
    session.commit()
    
    # Retrieve the labeled payload
    session.refresh(labeled_payload)
    assert labeled_payload.payload == payload_text
    assert labeled_payload.label_name == label_name
    assert labeled_payload.topic_name == topic_name
    assert labeled_payload.label.name == label_name
    assert labeled_payload.topic.name == topic_name
    assert isinstance(labeled_payload.id, str)
    assert isinstance(labeled_payload.created_at, datetime)


def test_relationships(session: Session):
    """Test the relationships between models."""
    # Create a topic
    topic_name = "test_topic"
    topic = Topic(name=topic_name)
    session.add(topic)
    
    # Create multiple labels for the topic
    label1 = Label(name="label1", topic_name=topic_name)
    label2 = Label(name="label2", topic_name=topic_name)
    session.add(label1)
    session.add(label2)
    session.commit()
    
    # Create labeled payloads
    payload1 = LabeledPayload(payload="payload1", label_name="label1", topic_name=topic_name)
    payload2 = LabeledPayload(payload="payload2", label_name="label1", topic_name=topic_name)
    payload3 = LabeledPayload(payload="payload3", label_name="label2", topic_name=topic_name)
    session.add(payload1)
    session.add(payload2)
    session.add(payload3)
    session.commit()
    
    # Test relationships
    session.refresh(topic)
    session.refresh(label1)
    session.refresh(label2)
    
    # Topic should have two labels
    assert len(topic.labels) == 2
    assert {label.name for label in topic.labels} == {"label1", "label2"}
    
    # Topic should have three examples
    assert len(topic.examples) == 3
    assert {example.payload for example in topic.examples} == {"payload1", "payload2", "payload3"}
    
    # Label1 should have two examples
    assert len(label1.examples) == 2
    assert {example.payload for example in label1.examples} == {"payload1", "payload2"}
    
    # Label2 should have one example
    assert len(label2.examples) == 1
    assert label2.examples[0].payload == "payload3"