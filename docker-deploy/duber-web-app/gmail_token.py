from google_auth_oauthlib.flow import InstalledAppFlow
import os
import logging

# 设置日志
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
REDIRECT_URI = os.getenv('GMAIL_REDIRECT_URI', 'http://localhost:40080/')

try:
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', 
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    creds = flow.run_local_server(
        port=40080,
        host='localhost',
        open_browser=True
    )
    
    # 保存凭证
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    logger.info("Token generated and saved successfully!")
except Exception as e:
    logger.error(f"Error during token generation: {str(e)}")
    raise
