from ailabel.db.crud import (
    get_label_statistics,
    get_recent_labeled_payloads,
)

from ailabel.lib.llms import generate_json


def label_payload(topic: str, payload: str):
    """Predict a label for a given payload in a topic."""

    def get_examples_for_topic(topic: str):
        topic_actual_labels = get_recent_labeled_payloads(topic)
        history = []
        for label in topic_actual_labels:
            history += [
                {"role": "user", "parts": [label.payload]},
                {"role": "assistant", "parts": [f'{{ "label": "{label.label_name}" }}']},
            ]
        return history

    def predict_label_for_payload(topic: str, payload: str):
        labels_for_topic = get_label_statistics(topic)
        distinct_labels = list(labels_for_topic.keys())
        if not distinct_labels:
            raise ValueError(f"Topic '{topic}' has no labels. Please label some payloads first.")

        # For multi-line input in batch mode, we need to adjust the system prompt
        history = get_examples_for_topic(topic)
        system_instruction = f"""Your task is to label incoming payloads for topic "{topic}".
                It is a classification task with the following possible labels: {distinct_labels}.
                Your response should have the format:
                {{ "label": "your-label-here" }}
                Where "your-label-here" is one of the possible labels for this topic.
                Example:
                {{ "label": "{distinct_labels[0]}" }}
                {{ "label": "{distinct_labels[1]}" }}"""

        predicted_label = generate_json(
            payload,
            history=history,
            system_instruction=system_instruction,
        )
        print(system_instruction)
        print(f"Predicted label: {predicted_label}")
        return predicted_label["label"]

    return predict_label_for_payload(topic, payload)
