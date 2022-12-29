import os, secrets, smtplib
from flask import url_for, current_app
from flask_login import current_user
from PIL import Image
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def save_picture(form_picture):
    random_name = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_name = random_name + f_ext
    picture_path = os.path.join(current_app.root_path, "static/images/profile_img", picture_name)
    
    output = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output)
    i.save(picture_path)

    if current_user.image_file != "default.jpg":
        os.remove(os.path.join(current_app.root_path, "static/images/profile_img", current_user.image_file))

    return picture_name


def send_reset_email(user):
    token = user.get_reset_token()
    smtp_email = current_app.config["SMTP_EMAIL"]
    smtp_host = current_app.config["SMTP_HOST"]
    smtp_psd = current_app.config["SMTP_PASSWORD"]
    smtp_port = current_app.config["SMTP_PORT"]
    smtp_from = current_app.config["SMTP_FROM"]
    smtp = smtplib.SMTP(host=smtp_host, port=smtp_port)
    smtp.starttls()
    smtp.login(smtp_email, smtp_psd)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "This is your instructions"
    msg["From"] = smtp_from
    msg["To"] = f"{user.email}"

    html = f"For reset password click to: <a href='{url_for('reset_token', token=token, _external=True)}' target='_blank' >Reset Link</a>"
    htmlMsg = MIMEText(html, "html")
    msg.attach(htmlMsg)
    
    smtp.sendmail(smtp_from, f"{user.email}", msg.as_string())
    smtp.quit()

