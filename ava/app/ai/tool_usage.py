import os
from openai import OpenAI
from pydantic import BaseModel

ticket = [{
  "id": 156956,
  "spam": False,
  "type": "Incident",
  "due_by": "2025-12-05T18:08:41Z",
  "source": 3,
  "status": 2,
  "deleted": False,
  "subject": "Need app installed",
  "category": None,
  "group_id": 5000064239,
  "priority": 1,
  "cc_emails": [],
  "fr_due_by": "2025-11-27T17:08:41Z",
  "to_emails": None,
  "created_at": "2025-11-26T18:08:38Z",
  "fwd_emails": [],
  "updated_at": "2025-11-26T18:08:41Z",
  "description": "<div style=\"font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica Neue,Arial,sans-serif; font-size: 14px; \"><div dir=\"ltr\">Can I please have FoxIT and Discord installed on my computer?</div></div>",
  "fr_escalated": False,
  "is_escalated": False,
  "requester_id": 5003345048,
  "responder_id": None,
  "sub_category": None,
  "workspace_id": 2,
  "custom_fields": {
    "sub_category_1": None,
    "sub_category_2": None,
    "business_impact": None,
    "issues_category": None,
    "revenue_impacting": None,
    "impacted_locations": None,
    "workflow_condition": None,
    "best_contact_method": None,
    "major_incident_type": None,
    "leaderboard_workflows": None,
    "status_page_incident_id": None,
    "amount_of_users_impacted": None,
    "no_of_customers_impacted": None,
    "when_did_the_issue_begin": None,
    "have_you_restarted_your_computer": None,
    "phone_number_of_point_of_contact": None,
    "if_remote_are_you_connected_to_vpn": None,
    "is_your_device_connected_to_the_internet": "No"
  },
  "department_id": 5000279522,
  "item_category": None,
  "email_config_id": None,
  "reply_cc_emails": [],
  "description_text": "Can I please have FoxIT and Discord installed on my computer?",
  "requested_for_id": 5003345048
}]

class Response(BaseModel):
    query_relevant_tickets: bool
    ticket_query_keywords: list[str]
    query_relevant_articles: bool
    article_query_keywords: list[str]

def tool_usage() -> dict:
    key = os.environ["OPENAIKEY"]
    client = OpenAI(api_key=key)

    ins = create_tool_usage_input(ticket)

    response = client.responses.parse(
            model="gpt-5.1",
            text_format=Response,
            instructions="Go ahead and let me know if querying either database is necessary and if so, go ahead and provide keywords to query the db with. Else for keywords return None or Null.",
            input=ins
            )

    print(response.output)

def create_tool_usage_input(ticket) -> list[dict]:
    ins = [
            {
                "role": "user",
                "content": str(ticket)
                }
            ]

    return ins
