ntfy API Subscription

This document outlines how to subscribe to ntfy topics using the API. You can subscribe via HTTP streams (JSON, SSE, raw) or WebSockets.

HTTP Stream

HTTP stream relies on a GET request with a streaming response. The connection stays open, sending messages as they arrive.

JSON Stream

Endpoint: <topic>/json

Returns a JSON stream, with one JSON message object per line. This is the recommended way to subscribe for most languages.

Example (curl):

curl -s ntfy.sh/disk-alerts/json
content_copy
download
Use code with caution.
Bash
SSE Stream

Endpoint: <topic>/sse

Returns messages as Server-Sent Events (SSE), suitable for use with EventSource.

Example (curl):

curl -s ntfy.sh/mytopic/sse
content_copy
download
Use code with caution.
Bash
Raw Stream

Endpoint: <topic>/raw

Returns messages as raw text, one line per message. Only includes the message body. Keepalive messages are sent as empty lines.

Example (curl):

curl -s ntfy.sh/disk-alerts/raw
content_copy
download
Use code with caution.
Bash
WebSockets

Endpoint: <topic>/ws

Returns messages as JSON objects (similar to the JSON stream).

Example (websocat):

websocat wss://ntfy.sh/mytopic/ws
content_copy
download
Use code with caution.
Bash
Advanced Features
Poll for Messages

Use the poll=1 query parameter to get available messages and close the connection. Can be combined with since=.

curl -s "ntfy.sh/mytopic/json?poll=1"
content_copy
download
Use code with caution.
Bash
Fetch Cached Messages

Use the since= query parameter to fetch cached messages. Values can be duration (e.g., 10m), Unix timestamp, a message ID, or all.

curl -s "ntfy.sh/mytopic/json?since=10m"
content_copy
download
Use code with caution.
Bash
Fetch Scheduled Messages

Use scheduled=1 (or sched=1) along with poll=1 to return scheduled messages.

curl -s "ntfy.sh/mytopic/json?poll=1&sched=1"
content_copy
download
Use code with caution.
Bash
Filter Messages

Filter messages using query parameters like id, message, title, priority, and tags. priority is a logical OR and tags is a logical AND.

curl "ntfy.sh/alerts/json?priority=high&tags=zfs-error"
content_copy
download
Use code with caution.
Bash

Available Filters:
| Filter Variable | Alias | Example | Description |
|-----------------|-----------------|-----------------------------------------------|-----------------------------------------------------------------------|
| id | X-ID | ntfy.sh/mytopic/json?poll=1&id=pbkiz8SD7ZxG | Only return messages that match this exact message ID |
| message | X-Message, m | ntfy.sh/mytopic/json?message=lalala | Only return messages that match this exact message string |
| title | X-Title, t | ntfy.sh/mytopic/json?title=some+title | Only return messages that match this exact title string |
| priority | X-Priority, prio, p| ntfy.sh/mytopic/json?p=high,urgent | Only return messages that match any priority listed (comma-separated) |
| tags | X-Tags, tag, ta| ntfy.sh/mytopic?/jsontags=error,alert | Only return messages that match all listed tags (comma-separated) |

Subscribe to Multiple Topics

Use a comma-separated list of topics in the URL.

curl -s ntfy.sh/mytopic1,mytopic2/json
content_copy
download
Use code with caution.
Bash
Authentication

Use Basic Auth or the auth query parameter for protected topics.

JSON Message Format

The /json and /sse endpoints return messages in JSON format.

Message Fields:

Field	Required	Type	Description
id	✔️	string	Randomly chosen message identifier
time	✔️	number	Message date time, as Unix timestamp
expires	(✔)️	number	Unix timestamp when the message will be deleted. Not set if Cache: no is sent.
event	✔️	string	open, keepalive, message, or poll_request. Typically, you'd be only interested in message events.
topic	✔️	string	Comma-separated list of topics the message is associated with.
message	-	string	Message body
title	-	string	Message title (defaults to ntfy.sh/<topic>)
tags	-	string array	List of tags
priority	-	1, 2, 3, 4, 5	Message priority (1=min, 3=default, 5=max)
click	-	URL	URL opened when the notification is clicked
actions	-	JSON array	Action buttons
attachment	-	JSON object	Attachment details (name, URL, size, etc.)

Attachment Fields:
| Field | Required | Type | Description |
|---------|----------|--------|------------------------------------------------------------------------------------|
| name | ✔️ | string | Name of the attachment. |
| url | ✔️ | URL | URL of the attachment. |
| type | - | string | Mime type of the attachment. Only defined if attachment was uploaded to the server. |
| size | - | number | Size of the attachment in bytes. Only defined if attachment was uploaded to server. |
| expires | - | number | Attachment expiry date as Unix timestamp, Only defined if attachment was uploaded to ntfy server.|

All Parameters
Parameter	Aliases (case-insensitive)	Description
poll	X-Poll, po	Return cached messages and close connection
since	X-Since, si	Return cached messages since timestamp, duration, or message ID
scheduled	X-Scheduled, sched	Include scheduled/delayed messages in the message list
id	X-ID	Filter: Only return messages that match this exact message ID
message	X-Message, m	Filter: Only return messages that match this exact message string
title	X-Title, t	Filter: Only return messages that match this exact title string
priority	X-Priority, prio, p	Filter: Only return messages that match any priority listed (comma-separated)
tags	X-Tags, tag, ta	Filter: Only return messages that match all listed tags (comma-separated)