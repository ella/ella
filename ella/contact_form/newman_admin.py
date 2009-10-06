from ella import newman
from ella.contact_form.models import Recipient, Message

newman.site.register((Recipient, Message))
