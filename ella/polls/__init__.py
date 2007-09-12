from ella.core.custom_urls import dispatcher
from ella.polls.models import Quiz

def quiz(request, bits, context):
    from ella.polls.views import QuizWizard
    quiz = context['object']
    return QuizWizard(quiz)(request)

dispatcher.register('take', quiz, model=Quiz)
