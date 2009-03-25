# -*- coding: cp1250 -*-
import base64
import os.path
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMENonMultipart import MIMENonMultipart
from email.Header import Header


def __uni2iso(text):
    return text.encode('iso-8859-2')


def __mimeImage(filename, msg, idim=None):
    fp = open(filename, 'rb')
    msgImage = MIMEImage(fp.read(), name=os.path.basename(filename))
    fp.close()
    if not idim:
        idim = '<%s>' % os.path.basename(filename)
    msgImage.add_header('Content-ID', idim)
    msg.attach(msgImage)
    return msgImage


def __mimeData(filename, msg):
    fp = open(filename, 'rb')
    data = MIMENonMultipart('application', 'pdf', name=os.path.basename(filename), charset='us-ascii')
    data.set_payload(base64.encodestring(fp.read()))
    data.add_header('Content-Transfer-Encoding', 'base64')
    fp.close()
    msg.attach(data)
    return data


def create_mail(**kwargs):
    '''
    Arguments:
    mailfrom
    mailto
    subject
    images [list]
    attachements [list]
    plaintext
    htmltext
    '''
    strFrom = kwargs.get('mailfrom')
    CHARSET = 'iso-8859-2'

    msgRoot = MIMEMultipart('related')
    msgRoot.add_header('X-Mailer', kwargs.get('xmailer', 'Ella CMS'))
    subj = Header(kwargs.get('subject', 'CMS E-mail'), CHARSET)
    msgRoot['Subject'] = subj
    msgRoot['From'] = strFrom
    msgRoot['To'] = kwargs.get('mailto', 'unknown@recipient.net')
    msgRoot.set_charset(CHARSET)
    msgRoot.preamble = 'This is a multi-part message in MIME format.'

    msgAlternative = MIMEMultipart('alternative')
    msgAlternative.set_charset(CHARSET)
    msgRoot.attach(msgAlternative)

    text = kwargs['plaintext']
    msgText = MIMEText(__uni2iso(text), 'plain', CHARSET)
    msgAlternative.attach(msgText)

    html = kwargs['htmltext']
    html = html.replace('UTF-8', CHARSET)
    msgText = MIMEText(__uni2iso(html), 'html', CHARSET)
    msgAlternative.attach(msgText)

    for img in kwargs.get('images', []):
        __mimeImage(img, msgRoot)
    for at in kwargs.get('attachements', []):
        __mimeData(at, msgRoot)
    return msgRoot
