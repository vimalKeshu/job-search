import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_sender.mailtrap.email_template import build_template

MAILTRIP_API_TOKEN="bf1ab73fc3"

def send_email(receiver, html, subject="Job recommendation", sender="Job Recommender <job.recommender@itjobsrecommender.org>"):
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = subject

    # Attach the HTML part
    message.attach(MIMEText(html, "html"))

    with smtplib.SMTP("bulk.smtp.mailtrap.io", 587) as server:
        server.starttls()
        server.login("api", MAILTRIP_API_TOKEN)
        server.sendmail(sender, receiver, message.as_string())
    print('email sent to ', receiver)

if __name__ == "__main__":
    receiver = "A Test User <it.jobs.recommender@gmail.com>"
    subject = "HTML Email without Attachment"
    send_email(receiver=receiver, subject=subject, html=build_template(job_html="""<li><a href="https://example.com/link1" style="color: #007bff; text-decoration: none;">Link 1</a></li>"""))
