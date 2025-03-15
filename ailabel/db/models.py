"""Database models for the ailabel application.

This module defines the SQLModel classes that represent the database schema:
- Topic: Represents a classification category (e.g., 'sentiment')
- Label: Represents a label within a topic (e.g., 'positive', 'negative')
- LabeledPayload: Represents a text payload with an assigned label

These models form the core data structure of the application and define
the relationships between topics, labels, and labeled data.
"""

import uuid
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime


class Topic(SQLModel, table=True):
    """A topic for classification.
    
    A topic represents a classification category, such as 'sentiment' or 'language'.
    Each topic can have multiple labels and labeled examples.
    
    Attributes:
        name: The unique name of the topic
        labels: Related labels for this topic
        examples: Labeled examples for this topic
    """
    name: str = Field(primary_key=True)
    labels: list["Label"] = Relationship(back_populates="topic")
    examples: list["LabeledPayload"] = Relationship(back_populates="topic")


class Label(SQLModel, table=True):
    """A label within a topic.
    
    A label represents a specific category within a topic, such as 'positive' or 'negative'.
    Each label belongs to a single topic and can have multiple examples.
    
    Attributes:
        name: The unique name of the label
        topic_name: The name of the topic this label belongs to
        topic: The related topic object
        examples: Labeled examples with this label
    """
    name: str = Field(primary_key=True)
    topic_name: str = Field(foreign_key="topic.name")
    topic: Optional[Topic] = Relationship(back_populates="labels")
    examples: list["LabeledPayload"] = Relationship(back_populates="label")


class LabeledPayload(SQLModel, table=True):
    """A text payload with an assigned label.
    
    A labeled payload represents a piece of text that has been assigned a label
    within a specific topic. This is the core data used for training and prediction.
    
    Attributes:
        id: Unique identifier for the labeled payload
        payload: The text content being labeled
        label_name: The name of the assigned label
        topic_name: The name of the topic
        created_at: When the labeled payload was created
        label: The related label object
        topic: The related topic object
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    payload: str
    label_name: str = Field(foreign_key="label.name")
    topic_name: str = Field(foreign_key="topic.name")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    label: Optional[Label] = Relationship(back_populates="examples")
    topic: Optional[Topic] = Relationship(back_populates="examples")
