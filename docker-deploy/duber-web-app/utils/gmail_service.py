import os.path
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
from django.conf import settings
from google.auth.transport.requests import Request

# 设置日志
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
# 修改重定向 URI，使用 localhost
REDIRECT_URI = os.getenv('GMAIL_REDIRECT_URI', 'http://localhost:8080/oauth2callback')

def get_oauth_flow():
    try:
        return Flow.from_client_secrets_file(
            'credentials.json',
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
    except Exception as e:
        logger.error(f"Error creating OAuth flow: {str(e)}")
        raise

def gmail_authenticate():
    creds = None
    try:
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    # 保存刷新后的凭证
                    with open('token.json', 'w') as token:
                        token.write(creds.to_json())
                except Exception as e:
                    logger.error(f"Error refreshing token: {str(e)}")
                    raise
            else:
                logger.error("No valid credentials available")
                raise Exception("Authentication required")
                    
        return build('gmail', 'v1', credentials=creds)
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise

def send_email(to_email, subject, message_text):
    """
    使用 Gmail API 发送邮件
    
    Args:
        to_email (str): 收件人邮箱
        subject (str): 邮件主题
        message_text (str): 邮件正文
        
    Returns:
        bool: 发送成功返回 True，失败返回 False
    """
    try:
        service = gmail_authenticate()
        message = MIMEMultipart('alternative')
        message['to'] = to_email
        message['subject'] = subject
        
        # 添加纯文本内容
        message.attach(MIMEText(message_text, 'plain'))
        
        # 转换为 base64 格式
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # 发送邮件
        service.users().messages().send(
            userId="me",
            body={'raw': raw}
        ).execute()
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email to {to_email}: {str(e)}")
        return False
