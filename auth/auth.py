import os
# Import necessary modules
from flask_jwt_extended import create_access_token, get_jwt_identity, unset_jwt_cookies, \
    set_access_cookies, verify_jwt_in_request

# Authentication class
class Authentication:

    __token = None

    def create_token(self, identity):
        # Create access token
        self.__token = create_access_token(identity=identity)
        return self.__token

    def refresh_token(self, identity):
        # Refresh access token
        self.create_token(identity)

    def validate_jwt(self):
        try:
            # Verify JWT in request
            verify_jwt_in_request()
        except Exception as e:
            return False
        return True

    def get_authenticated_user(self):
        if self.validate_jwt():
            # Get authenticated user from JWT
            return get_jwt_identity()
        return None

    def set_cookie(self, response, access_token):
        # Set access token as cookie
        set_access_cookies(response, access_token)

    def unset_cookie(self, response, access_token):
        # Unset access token cookie
        unset_jwt_cookies(response, access_token)
