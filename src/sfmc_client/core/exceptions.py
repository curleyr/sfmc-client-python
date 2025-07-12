# --- core/exceptions.py ---

class SFMCAPIError(Exception):
    """Base exception class for Salesforce Marketing Cloud API errors."""
    pass


class AuthenticationError(SFMCAPIError):
    """Raised when authentication with the Salesforce Marketing Cloud API fails."""
    pass


class RequestError(SFMCAPIError):
    """Raised when a REST or SOAP API request fails.""" 
    pass
