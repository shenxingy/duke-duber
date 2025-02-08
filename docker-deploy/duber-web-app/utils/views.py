from django.shortcuts import redirect
from django.conf import settings
from .gmail_service import get_oauth_flow
import json
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

def start_oauth_flow(request):
    flow = get_oauth_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    request.session['oauth_state'] = state
    return redirect(authorization_url)

def oauth2_callback(request):
    try:
        logger.info("OAuth callback received")
        
        # 验证 state
        session_state = request.session.get('oauth_state')
        request_state = request.GET.get('state')
        
        if not session_state or session_state != request_state:
            logger.error("Invalid OAuth state")
            messages.error(request, 'Authentication failed: Invalid state')
            return redirect('driver_dashboard')
        
        flow = get_oauth_flow()
        flow.fetch_token(
            authorization_response=request.build_absolute_uri(),
        )
        
        credentials = flow.credentials
        logger.info("Got credentials, saving token...")
        
        try:
            with open('token.json', 'w') as token:
                token.write(credentials.to_json())
            logger.info("Token saved successfully!")
            messages.success(request, 'Authentication successful')
        except Exception as e:
            logger.error(f"Error saving token: {str(e)}")
            messages.error(request, 'Failed to save authentication token')
            
        return redirect('driver_dashboard')
    except Exception as e:
        logger.error(f"Error in oauth2_callback: {str(e)}")
        messages.error(request, 'Authentication failed')
        return redirect('driver_dashboard')
