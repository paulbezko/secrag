from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app

import smtplib

def send_email_from_template(email, template, payload):

    head = f"""
        <head>
            <style>
                .container {{
                    font-family: Arial, sans-serif;
                    color: #333;
                    background-color: #f9f9f9;
                    padding: 30px;
                    max-width: 400px;
                    margin: auto;
                    border-radius: 8px;
                    border: 1px solid #ddd;
                }}
                .header {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #333;
                    text-align: center;
                }}
                .content {{
                    font-size: 16px;
                    line-height: 1.6;
                    text-align: center;
                    color: #555;
                    margin-top: 20px;
                }}
                .button-container {{
                    text-align: center;
                    margin-top: 30px;
                }}
                .button {{
                    background-color: #FFC107;
                    color: #2D2D2D;
                    padding: 12px 24px;
                    border-radius: 5px;
                    text-decoration: none;
                    font-weight: bold;
                    font-size: 16px;
                }}
                a:link, span.MsoHyperlink {{
                    mso-style-priority:100 !important;
                    color:#000000 !important;
                    color:#000000;
                    text-decoration:none !important;
                }}
                .signature {{
                    font-size: 14px;
                    color: #333;
                    text-align: center;
                    margin-top: 30px;
                }}
                .footer {{
                    font-size: 12px;
                    color: #777;
                    text-align: center;
                    margin-top: 20px;
                }}
            </style>
        </head>
    """
    
    # Define HTML templates for each email type
    templates = {
        'signUp': {
            'subject': 'Welcome to SECRAG!',
            'html_body': f"""
                <html>
                    {head}
                    <body>
                        <div class="container">
                            <div class="header">Welcome to SECRAG!</div>
                            <div class="content">
                                To proceed with setting up your account, please confirm by clicking the button below.
                            </div>
                            <div class="button-container">
                                <a class="button" href="http://localhost:8080/change-email?token={payload}">Confirm Email</a>
                            </div>
                            <div class="signature">Warm regards,<br>SECRAG Team</div>
                            <div class="footer">If you did not sign up for this account, please disregard this message.</div>
                        </div>
                    </body>
                </html>
            """
        },
        'resetPassword': {
            'subject': 'Reset Password',
            'html_body': f"""
                <html>
                    {head}
                    <body>
                        <div class="container">
                            <div class="header">Reset Your Password</div>
                            <div class="content">
                                To complete your request to reset your password, please confirm by clicking the button below.
                            </div>
                            <div class="button-container">
                                <a class="button" href="http://localhost:8080/change-email?token={payload}">Confirm Email</a>
                            </div>
                            <div class="signature">Warm regards,<br>SECRAG Team</div>
                            <div class="footer">If you did not request this change, please disregard this message.</div>
                        </div>
                    </body>
                </html>
            """
        },
        'changeEmail': {
            'subject': 'Change Email Confirmation',
            'html_body': f"""
                <html>
                    {head}
                    <body>
                        <div class="container">
                            <div class="header">Confirm Your Email Address</div>
                            <div class="content">
                                To complete your request to update your email address, please confirm by clicking the button below.
                            </div>
                            <div class="button-container">
                                <a class="button" href="http://localhost:8080/change-email?token={payload}">Confirm Email</a>
                            </div>
                            <div class="signature">Warm regards,<br>SECRAG Team</div>
                            <div class="footer">If you did not request this change, please disregard this message.</div>
                        </div>
                    </body>
                </html>
            """
        },
        'subscribe': {
            'subject': 'Subscription Successful',
            'html_body': f"""
                <html>
                    {head}
                    <body>
                        <div class="container">
                            <div class="header">Your Subscription Was Successful</div>
                            <div class="content">
                                You can now access SECRAG's features in accordance with your subscription.
                            </div>
                            <div class="signature">Warm regards,<br>SECRAG Team</div>
                            <div class="footer">If you did not adjust your subscription, please disregard this message.</div>
                        </div>
                    </body>
                </html>
            """
        },
        'unsubscribe': {
            'subject': 'Unsubscription Successful',
            'html_body': f"""
                <html>
                    {head}
                    <body>
                        <div class="container">
                            <div class="header">Your Unsubscription Was Successful</div>
                            <div class="content">
                                Thank you for using SECRAG!
                            </div>
                            <div class="signature">Warm regards,<br>SECRAG Team</div>
                            <div class="footer">If you did not adjust your subscription, please disregard this message.</div>
                        </div>
                    </body>
                </html>
            """
        },
        'purchase': {
            'subject': 'Token Purchase Successful',
            'html_body': f"""
                <html>
                    {head}
                    <body>
                        <div class="container">
                            <div class="header">Your Token Purchase Was Successful</div>
                            <div class="content">
                                Your token balance has been updated.
                            </div>
                            <div class="signature">Warm regards,<br>SECRAG Team</div>
                            <div class="footer">If you did not purchase tokens, please disregard this message.</div>
                        </div>
                    </body>
                </html>
            """
        }
    }

    # Extract subject and body
    subject = templates[template]['subject']
    html_body = templates[template]['html_body']

    try:
        # Create a multipart email
        email_message = MIMEMultipart('alternative')
        email_message['Subject'] = subject
        email_message['From'] = 'secrag.info@gmail.com'
        email_message['To'] = email
        
        # Attach the HTML version
        email_message.attach(MIMEText(html_body, 'html'))

        # Send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login('secrag.info@gmail.com', 'ireb koiu wlwy wsco')
            smtp_server.send_message(email_message)

    except Exception as error:
        print(error)

recipient = "paul.bezko@hotmail.com"

list_templates = ['signUp', 'resetPassword', 'changeEmail', 'subscribe', 'unsubscribe', 'purchase']
for template in list_templates:
    send_email_from_template(recipient, template, 12345)