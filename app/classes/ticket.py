class Ticket:
    def __init__(self, id, requester_name, requester_email, department, subject, description, last_ai_gen, ai_attempts, conversations, ticket_created, time_last_message_recieved, time_last_ai_message_post, post_email, post_note, put_fields, closed):
        self.id = id
        self.requester_name = requester_name
        self.requester_email = requester_email
        self.department = department
        self.subject = subject
        self.description = description
        self.last_ai_gen = last_ai_gen
        self.ai_attempts = ai_attempts
        self.conversations = conversations
        self.ticket_created = ticket_created
        self.time_last_message_recieved = time_last_message_recieved
        self.time_last_ai_message_post = time_last_ai_message_post
        self.post_email = post_email
        self.post_note = post_note
        self.put_fields = put_fields
        self.closed = closed
