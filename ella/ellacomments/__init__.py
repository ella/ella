"""  
Change the attributes you want to customize
"""  
     
from threadedcomments.models import ThreadedComment
from ella.ellacomments.forms import EllaCommmentForm
     
def get_model():
    return ThreadedComment
     
def get_form():
    return EllaCommmentForm

