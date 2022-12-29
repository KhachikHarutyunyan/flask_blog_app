import os
basedir = os.path.abspath(os.path.dirname(__file__))

# in production set environ
# os.environe.get("SMTP_EMAIL")

class Config:
    SECRET_KEY = "84d2f2dd07c0132c3ed17b8830100562"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "site.db")
    SMTP_EMAIL = "dena.wyman@ethereal.email"
    SMTP_HOST = "smtp.ethereal.email"
    SMTP_PASSWORD = "dXBR8zVPpPbWnEYbXX"
    SMTP_PORT = 587
    SMTP_FROM = "blogapp@gmail.com"

