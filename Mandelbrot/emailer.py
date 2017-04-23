import smtplib

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


def email(dest):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = 'Fractal Image'
        msg['From'] = 'whatwhat5597@gmail.com'
        msg['To'] = dest

        file = 'screen.png'
        with open(file, 'rb') as fp:
            img = MIMEImage(fp.read())
        msg.attach(img)

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login('whatwhat5597@gmail.com', '')
        s.sendmail('whatwhat5597@gmail.com', dest, msg.as_string())
        s.quit()
        return 0
    except:
        return 1
