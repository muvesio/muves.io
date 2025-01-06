from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.cloud import secretmanager

import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

project_id = "muves-website"  # Replace with your actual project ID

def access_secret_version(project_id, secret_id, version_id="latest"):
    """
    Access the payload for the given secret version
    if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = rf"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})

    # Print the secret payload.

    #
    # For more details on how to parse the payload, please see the API
    # documentation for the AccessSecretVersion response.
    payload = response.payload.data.decode("UTF-8")
    return payload

# Email Configuration (Replace with your credentials)
EMAIL_ADDRESS = access_secret_version(project_id, "EMAIL_ADDRESS")  # Use environment variables for security
EMAIL_PASSWORD = access_secret_version(project_id, "EMAIL_PASSWORD")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com") # Example: smtp.gmail.com, smtp.office365.com, etc.
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587)) # Example: 587 (TLS), 465 (SSL)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/privacy", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})

@app.post("/send-email", response_class=HTMLResponse)
async def send_email(request: Request, name: str = Form(...), company: str = Form(None), email: str = Form(...)):
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = EMAIL_ADDRESS
        message["To"] = EMAIL_ADDRESS
        message["Subject"] = "New Waiting List Submission"

        # Email body
        body = f"Name: {name}\nCompany: {company}\nEmail: {email}"
        message.attach(MIMEText(body, "plain"))

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Start TLS encryption
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(message)

        return templates.TemplateResponse("index.html", {"request": request, "message": "Thank you for joining the waiting list!", "message_type": "success"})

    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "message": f"Error sending email: {e}", "message_type": "error"})