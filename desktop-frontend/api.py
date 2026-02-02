"""
API Utility Module
Handles authentication and API requests with token management.
"""
import requests
from typing import Optional, Dict, Any


class APIClient:
    """Singleton API client that manages authentication and requests."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_url = "http://127.0.0.1:8000"
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._initialized = True
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self._access_token is not None
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get headers with authorization if authenticated."""
        headers = {"Content-Type": "application/json"}
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        return headers
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and store tokens.
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            Dict with success status and message
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/token/",
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self._access_token = data.get("access")
                self._refresh_token = data.get("refresh")
                return {"success": True, "message": "Login successful"}
            
            elif response.status_code == 401:
                return {"success": False, "message": "Invalid username or password"}
            
            else:
                return {"success": False, "message": f"Login failed: {response.status_code}"}
                
        except requests.exceptions.ConnectionError:
            return {"success": False, "message": "Cannot connect to server"}
        except requests.exceptions.Timeout:
            return {"success": False, "message": "Request timed out"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def logout(self):
        """Clear stored tokens."""
        self._access_token = None
        self._refresh_token = None
    
    def refresh_access_token(self) -> bool:
        """
        Refresh the access token using refresh token.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._refresh_token:
            return False
            
        try:
            response = requests.post(
                f"{self.base_url}/api/token/refresh/",
                json={"refresh": self._refresh_token},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self._access_token = data.get("access")
                return True
            return False
            
        except Exception:
            return False
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """
        Make authenticated GET request.
        
        Args:
            endpoint: API endpoint (e.g., "/api/summary/")
            params: Optional query parameters
            
        Returns:
            Response object
        """
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()
        headers.pop("Content-Type", None)  # Not needed for GET
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        # Try to refresh token on 401
        if response.status_code == 401 and self._refresh_token:
            if self.refresh_access_token():
                headers["Authorization"] = f"Bearer {self._access_token}"
                response = requests.get(url, headers=headers, params=params, timeout=10)
        
        return response
    
    def post(self, endpoint: str, data: Optional[Dict] = None, 
             files: Optional[Dict] = None) -> requests.Response:
        """
        Make authenticated POST request.
        
        Args:
            endpoint: API endpoint
            data: JSON data to send
            files: Files to upload
            
        Returns:
            Response object
        """
        url = f"{self.base_url}{endpoint}"
        
        if files:
            # For file uploads, don't set Content-Type (let requests handle it)
            headers = {}
            if self._access_token:
                headers["Authorization"] = f"Bearer {self._access_token}"
            response = requests.post(url, headers=headers, files=files, timeout=30)
        else:
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
        
        # Try to refresh token on 401
        if response.status_code == 401 and self._refresh_token:
            if self.refresh_access_token():
                if files:
                    headers["Authorization"] = f"Bearer {self._access_token}"
                    response = requests.post(url, headers=headers, files=files, timeout=30)
                else:
                    response = requests.post(url, headers=self.headers, json=data, timeout=10)
        
        return response


# Global API client instance
api = APIClient()
