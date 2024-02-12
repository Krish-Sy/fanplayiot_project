from googleapiclient import discovery
from models import Attendee  
from flask import current_app 
from config import Config

API_KEY = Config.API_KEY

client = discovery.build(
  "commentanalyzer",
  "v1alpha1",
  developerKey=API_KEY,
  discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
  static_discovery=False,
)

def filter_questions(event_id) :
    appropriate_questions = []
    with current_app.app_context():
        eventAttendees = Attendee.query.filter_by(event_id = event_id).all()
        for eventAttendee in eventAttendees:
            question = eventAttendee.question
            analyze_request = {
                'comment': {'text': question},
                'requestedAttributes': {'TOXICITY': {}}
            }
            response = client.comments().analyze(body=analyze_request).execute()
            toxicity_score = response['attributeScores']['TOXICITY']['summaryScore']['value']
            if toxicity_score < 0.5:
                appropriate_questions.append(question)

        print(appropriate_questions)
        return appropriate_questions




