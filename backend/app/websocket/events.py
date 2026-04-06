# app/websocket/events.py

from enum import StrEnum


class FeedEventType(StrEnum):
    PROJECT_CREATED = "project_created"
    MILESTONE_POSTED = "milestone_posted"
    PROJECT_COMPLETED = "project_completed"
    COMMENT_POSTED = "comment_posted"
    COLLAB_REQUEST = "collab_request"


# All events are serialised as JSON with the following shape:
# {
#     "type": FeedEventType,
#     "timestamp": "<ISO 8601>",
#     ...payload fields specific to each event type
# }
#
# Event payloads by type:
#
# project_created:
#     project_id, owner_id, title
#
# milestone_posted:
#     project_id, owner_id, milestone_title
#
# project_completed:
#     project_id, owner_id, title
#
# comment_posted:
#     project_id, author_id
#
# collab_request:
#     project_id, requester_id