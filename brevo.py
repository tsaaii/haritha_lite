import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime

def send_report_email(to_email, subject, body, attachment_path):
    # Brevo SMTP details
    smtp_server = 'smtp-relay.brevo.com'  # check your Brevo dashboard
    smtp_port = 587
    smtp_username = '90c222001@smtp-brevo.com'
    smtp_password = '9q0xOFCIrgUkz6Ef'

    from_email = 'noreply@advitiaum.com'

    # Create email
    msg = MIMEMultipart()
    msg['From'] = 'Advitia Labs <noreply@advitiaum.com>'

    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach body
    msg.attach(MIMEText(body, 'plain'))

    # Attach file
    if attachment_path:
        part = MIMEBase('application', 'octet-stream')
        with open(attachment_path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        f'attachment; filename="{attachment_path.split("/")[-1]}"')
        msg.attach(part)

    # Send email
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()

today_date = datetime.now().strftime('%d-%m-%Y')
# Example usage
send_report_email(
    to_email='swachhaandhra2015@gmail.com',
    #to_email='saaitejaa@gmail.com',
    #to_email='prasadraju.ca@gmail.com',
    #subject=f'{today_date} Legacy report',
    subject='07-07-2025 Legacy report',
    body='Hello, Please find the Legacy waste remediation report below. Thank you.',
    attachment_path='/Users/loislabs/Downloads/Ferndale/tmp/output/07-07-2025-Report.pdf'
)
