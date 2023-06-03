from cgitb import text
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from unicodedata import name
class mail:
    def send_mail(sender_address,sender_pass,receiver_address, username, password, name):
        #Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'Login Credentials for CarCare, India'
        mail_content='''Dear '''+name+''',
                        \nThese are the credentials for CarCare login:
                        \nUserName: '''+username+'''
                        \nPassword: '''+password+'''
                        \n\nRegards'''
        #The subject line
        # #The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'plain'))
        #Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(sender_address, sender_pass) #login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
        #print('Mail Sent')


