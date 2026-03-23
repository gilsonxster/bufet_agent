import os
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists('credentials.json'):
                import json
                try:
                    with open('credentials.json', 'r') as f:
                        data = json.load(f)
                    if data.get('type') == 'service_account':
                        creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                        creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Error reading credentials.json: {e}")
                    return None
            elif os.path.exists('service_account.json'):
                creds = service_account.Credentials.from_service_account_file('service_account.json', scopes=SCOPES)
            else:
                print("No Drive API credentials found. Please provide credentials.json or service_account.json.")
                return None
                
        if creds and not isinstance(creds, service_account.Credentials):
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                
    return build('drive', 'v3', credentials=creds)

def upload_to_drive(content, file_name, folder_id):
    try:
        service = get_drive_service()
        if not service:
            return None
        
        temp_file_path = f"tmp_{file_name}"
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(temp_file_path, mimetype='text/markdown', resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
        return file.get('id')
    except Exception as e:
        print(f"Error uploading to drive: {e}")
        return None

def is_authenticated():
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            if creds.valid:
                return True
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                return True
        except Exception:
            return False
            
    if os.path.exists('service_account.json'):
        return True
        
    if os.path.exists('credentials.json'):
        import json
        try:
            with open('credentials.json', 'r') as f:
                data = json.load(f)
            if data.get('type') == 'service_account':
                return True
        except:
            pass
            
    return False

def list_drive_files(folder_id):
    try:
        service = get_drive_service()
        if not service:
            return []
        
        query = f"'{folder_id}' in parents and trashed=false"
        results = service.files().list(q=query, fields="nextPageToken, files(id, name, createdTime)", orderBy="createdTime desc").execute()
        return results.get('files', [])
    except Exception as e:
        print(f"Error listing files: {e}")
        return []

def get_drive_file_content(file_id):
    try:
        service = get_drive_service()
        if not service:
            return None
        
        request = service.files().get_media(fileId=file_id)
        file_content = request.execute()
        return file_content.decode('utf-8')
    except Exception as e:
        print(f"Error downloading file content: {e}")
        return None
