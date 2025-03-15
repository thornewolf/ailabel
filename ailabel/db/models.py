import uuid
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime


class Topic(SQLModel, table=True):
    name: str = Field(primary_key=True)
    labels: list["Label"] = Relationship(back_populates="topic")
    examples: list["LabeledPayload"] = Relationship(back_populates="topic")


class Label(SQLModel, table=True):
    name: str = Field(primary_key=True)
    topic_name: str = Field(foreign_key="topic.name")
    topic: Optional[Topic] = Relationship(back_populates="labels")
    examples: list["LabeledPayload"] = Relationship(back_populates="label")


class LabeledPayload(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    payload: str
    label_name: str = Field(foreign_key="label.name")
    topic_name: str = Field(foreign_key="topic.name")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    label: Optional[Label] = Relationship(back_populates="examples")
    topic: Optional[Topic] = Relationship(back_populates="examples")
