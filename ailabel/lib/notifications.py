import requests

"""
Module for sending notifications via ntfy.sh service.

This module provides functionality to send push notifications through the ntfy.sh
web service. Ntfy.sh is a pub-sub notification service that allows sending
notifications to various devices and platforms.

The module will contain methods for:
- Sending push notifications
- Configuring notification parameters
- Managing notification topics/channels
"""


def send_notification(topic: str, message: str):
    """
    Send a notification to a webhook URL with a message.

    Args:
        url (str): The webhook URL to send the notification to
        message (str): The message content to send
    """
    try:
        response = requests.post(f"https://ntfy.sh/{topic}", data=message.encode("utf-8"))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send notification: {e}")


if __name__ == "__main__":
    topic = "thornewolf"
    message = "Hello, this is a test notification!"
    send_notification(topic, message)
