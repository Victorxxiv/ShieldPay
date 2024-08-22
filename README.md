# ShieldPay

Webstack Portfolio Project

By
Name: Victor Mwendwa
Email: <victormwendwa804@gmail.com>

ShieldPay is

## 1. Get All Users

- Purpose: Retrieves a list of all registered users.
- Method: GET
- URL: `/user`

## 2. Login User

- Purpose Authenticates a user and returns a JWT token.
- Method: POST
- URL: `/login`
- Request Parameters:
  - Body:
    - `email` (string, required): The email of the user.
    - `password` (string, required): The password of the user.

## 3. Get All Users (Authenticated)

- Purpose: Retrieves a list of all users (requires a valid JWT token).
- Method: GET
- URL: `/user`
- Headers:
  - `x-access-token` (string, required): The JWT token obtained after logging in.

## 4. Signup New User

- Purpose: Registers a new user in the system.
- Method: POST
- URL: `/signup`
- Request Parameters:
  - Body:
    - `name` (string, required): The name of the user.
    - `email` (string, required): The email of the user.
    - `password` (string, required): The password of the user.
      Response:
- 201 Created: User successfully registered.
  json
  {
  "message": "Successfully registered"
  }
  - 400 Bad Request: Missing required data.
    json
    {
    "message": "Missing data"
    }

  - 202 Accepted: User already exists.
    json
    {
    "message": "User already exists. Please log in."
    }


Static Files:

Endpoint: static
URL Rule: /static/<path:filename>
Methods: OPTIONS, HEAD, GET
User Registration:

Endpoint: app_views.register_user
URL Rule: /api/v1/views/register
Methods: OPTIONS, POST
User Login:

Endpoint: app_views.login_user
URL Rule: /api/v1/views/login
Methods: OPTIONS, POST
Get User Profile:

Endpoint: app_views.get_user
URL Rule: /api/v1/views/profile
Methods: OPTIONS, HEAD, GET
User Logout:

Endpoint: app_views.logout
URL Rule: /api/v1/views/logout
Methods: OPTIONS, POST
Home Page:

Endpoint: home
URL Rule: /
Methods: OPTIONS, HEAD, GET
Health Check:

Endpoint: health
URL Rule: /health
Methods: OPTIONS, HEAD, GET