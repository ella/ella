interview_test = """
=========
INTERVIEW
=========

>>> from ella.interviews import models, views
>>> from django.test.client import Client
>>> from django.core.urlresolvers import reverse
>>> from datetime import datetime, timedelta

>>> now = datetime.now()


Database models
---------------
>>> models.Interview.objects.all()
[<Interview: int 1>, <Interview: int 2>]

>>> i1 = models.Interview.objects.get(pk=1)
>>> i1
<Interview: int 1>


"Ask" methods
-------------

# Before
>>> i1.ask_from = now + timedelta(5)
>>> i1.ask_to = now + timedelta(10)
>>> i1.asking_started()
False
>>> i1.asking_ended()
False
>>> i1.can_ask()
False

# In the middle
>>> i1.ask_from = now - timedelta(10)
>>> i1.ask_to = now + timedelta(10)
>>> i1.asking_started()
True
>>> i1.asking_ended()
False
>>> i1.can_ask()
True

# After
>>> i1.ask_from = now - timedelta(10)
>>> i1.ask_to = now - timedelta(5)
>>> i1.asking_started()
True
>>> i1.asking_ended()
True
>>> i1.can_ask()
False


Reply methods
-------------
# Before
>>> i1.reply_from = now + timedelta(5)
>>> i1.reply_to = now + timedelta(10)
>>> i1.replying_started()
False
>>> i1.replying_ended()
False
>>> i1.can_reply()
False

# In the middle
>>> i1.reply_from = now - timedelta(10)
>>> i1.reply_to = now + timedelta(10)
>>> i1.replying_started()
True
>>> i1.replying_ended()
False
>>> i1.can_reply()
True

# After
>>> i1.reply_from = now - timedelta(10)
>>> i1.reply_to = now - timedelta(5)
>>> i1.replying_started()
True
>>> i1.replying_ended()
True
>>> i1.can_reply()
False



Asking cycle
------------

# Before asking ended...
>>> i1.ask_to = now + timedelta(1)
>>> i1.asking_ended()
False
>>> q1 = models.Question(interview=i1, content='How are you?', nickname='nick1', email='eml@example.net')
>>> q1.save()
>>> q2 = models.Question(interview=i1, content='Where are you?', nickname='nick2', email='lme@example.net')
>>> q2.save()

# Before replying started...
>>> i1.reply_from = now + timedelta(1)
>>> i1.can_reply()
False
>>> i1.get_questions()
[<Question: Where are you?>, <Question: How are you?>]

# After asking ended...
>>> i1.ask_to = now - timedelta(1)
>>> i1.asking_ended()
True
>>> i1.get_questions()
[<Question: How are you?>, <Question: Where are you?>]

# After replying started...
>>> i1.reply_from = now - timedelta(1)
>>> i1.get_questions()
[]

>>> i1.unanswered_questions()
[<Question: How are you?>, <Question: Where are you?>]



Interviewee
-----------
>>> models.Interviewee.objects.all()
[<Interviewee: Bill>]

>>> iee1 = models.Interviewee.objects.get(pk=1)
>>> iee1
<Interviewee: Bill>

Answer
------
>>> a1 = models.Answer(question=q1, interviewee=iee1, content='Fine!')
>>> a1.save()

Question
--------
>>> q1 = models.Question.objects.get(pk=1)
>>> q1.author
u'nick1'
>>> q1.answers
[<Answer: Answer object>]
>>> q1.answered()
True

>>> q2 = models.Question.objects.get(pk=2)
>>> q2.author
u'nick2'
>>> q2.answers
[]
>>> q2.answered()
False


VIEWS
=====
>>> url = i1.get_absolute_url()
>>> url
'/2000/1/1/interviews/int-1/'

>>> cl1 = Client()
>>> resp = cl1.get(url)
>>> resp.status_code
200



"""

__test__ = {
    'interview_test': interview_test,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()
