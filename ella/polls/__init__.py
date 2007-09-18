from ella.core.custom_urls import dispatcher
from ella.polls.models import Quiz, Contest

def contest(request, context):
    from ella.polls.views import ContestWizard
    contest = context['object']
    return ContestWizard(contest)(request)

def quiz(request, context):
    from ella.polls.views import QuizWizard
    quiz = context['object']
    return QuizWizard(quiz)(request)

dispatcher.register_custom_detail(Quiz, quiz)
dispatcher.register_custom_detail(Contest, contest)
