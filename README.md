# ShieldPay Documentation

Webstack Portfolio Project

By
Name: Victor Mwendwa
Email: <victormwendwa804@gmail.com>

## Overview

ShieldPay is a flask framework based payment system that facilitates Third Party Payments using the Escrow Model and Technology.

## Backend Structure

This document provides an explanation of the backend structure of ShieldPay.

ShieldPay/tree/main/api/v1/views/user
This path contains routes/endpoints for handling Registration, Login, User Profile, and Logout.

ShieldPay/tree/main/api/v1/views/transactions
This path contains routes/endpoints for handling transactions.

### User_Views

@app_views.route('/register', methods=\['POST'\])
Function: register_user()

Input Data Validation: Retrieves registration data from the JSON payload. Checks for required fields (email, password, first_name, last_name, phone_number, location). Returns a 400 error if any field is missing.

User Registration: Checks if the user with the provided email already exists. Returns a 409 error if the user exists, or proceeds to create a new user if not.

Account Creation: Calls account_service.create_account() to initialize an account for the user with zero funds and sets user_id.

Response: Returns a JSON response with a 201 status code, including user details and account information.

@app_views.route('/login', methods=\['POST'\])
Function: login_user()

Data Extraction: Extracts email, phone_number, and password from the request data.

Input Validation: Checks for either email or phone_number and password. Returns a 400 error if any are missing.

User Retrieval: Retrieves the user based on provided identifier.

User Existence Check: Checks if the user exists. Returns a 404 error if not found.

Password Verification: Verifies the password. Returns a 400 error if incorrect.

Token Creation and Cookie Setting: Creates an access token and sets it as a cookie.

Response: Returns a JSON response with a 200 status code on successful login.

@app_views.route('/profile', methods=\['GET'\])
Function: get_user()

JWT Authentication: Requires a valid JWT token. Extracts user_id from the token.

User Existence Check: Checks if the user exists. Returns a 404 error if not found.

Response: Returns user details as a JSON response with a 200 status code.

@app_views.route('/logout', methods=\['POST'\])
Function: logout()

Handles logout by removing the access token from the response.

### Transact_View

@user_trans.route('/transact', methods=\['POST'\])
Function: create_transaction()

Functionality: Creates a new transaction. Requires a JWT token.

@user_trans.route('/transactions', methods=\['GET'\])
Function: get_all_transactions()

Functionality: Retrieves all transactions for the authenticated user. Requires JWT token.

Get authenticated user's ID.
Retrieve all transactions.
Return a list of transactions.
@user_trans.route('/transaction/<int:transaction_id>', methods=\['GET'\])
Function: get_transaction(transaction_id)

Functionality: Retrieves a transaction by ID.

Get transaction by ID.
Return 404 if not found, otherwise return transaction details.
@user_trans.route('/approve/<string:transaction_id>', methods=\['PATCH'\])
Function: approve_transaction(transaction_id)

Functionality: Approves a transaction.

Get transaction by ID.
Check if pending.
Transfer funds and approve transaction.
Return success or error message.
@user_trans.route('/cancel/<string:transaction_id>', methods=\['PATCH'\])
Function: cancel_transaction(transaction_id)

Functionality: Cancels a transaction.

Get transaction by ID.
Check if pending.
Create conflict if necessary.
Return success or error message.
@user_trans.route('/deposit')
@user_trans.route('/withdraw')

Routes for deposit and withdraw operations.

## Auth

### Class: Authentication

\_\_token Attribute: Stores the access token.

Methods:

create_token(self, identity): Creates and returns a new access token.
refresh_token(self, identity): Intended to refresh the token but doesn’t update the \_\_token attribute.
validate_jwt(self): Validates JWT in the request.
get_authenticated_user(self): Retrieves the identity from a valid JWT.
set_cookie(self, response, access_token): Sets access token as a cookie.
unset_cookie(self, response, access_token): Removes the access token cookie.

### User_Auth

Class: UserAuth

Methods:
hash_password(self, password): Hashes and salts passwords.
verify_password(self, candidate_password, hashed_password): Verifies passwords.
create_user(self, \*\*kwargs): Creates a new user.
get_user_by_email(self, email): Retrieves user by email.
get_user_by_phone_number(self, phone_number): Retrieves user by phone number.
get_user_by_id(self, id): Retrieves user by ID.
get_all_users(self): Retrieves all users.
delete_user(self, id): Deletes user by ID.
update_user(self, id, email, password): Updates user details.

### Verify_User

Function: generate_verification_token()

Generates a URL-safe verification token.
Function: send_verification_email(user_email, verification_token)

Sends a verification email with a token.
Returns success or error message.

## db

### init

Function: Initializes the database and session.

### Storage

Class: DB

Attributes:

\_\_engine: Manages database connections.
\_\_session: Manages database sessions.
Constructor: Initializes connection parameters and creates tables.

## models

### Accounts

Class: Accounts

Table Configuration: Represents the 'accounts' table in the database.

## Utils

### Admin

This utility/service class handles administrative tasks in the ShieldPay system.

Class Attributes:

db: An instance of the DB class, initialized when an Admin instance is created.
Methods:

get_all_transactions(): Retrieves all transactions from the database using the Transactions SQLAlchemy model. It assumes the db attribute provides a query method for database operations.

get_all_accounts(): Retrieves all accounts from the database using the Accounts SQLAlchemy model.

get_all_users(): Retrieves all users from the database using the User SQLAlchemy model.

### GetRelationships

This class retrieves related information from different tables in the ShieldPay database.

Class Attributes:

\_\_db: An instance of the DB class, initialized when a GetRelationships instance is created.
Methods:

get_user_from_accounts(account_id): Retrieves the user associated with a given account ID from the Accounts table. Assumes the Accounts model has a user attribute.

get_account_from_user(user_id): Retrieves the account associated with a given user ID from the User table. Assumes the User model has an accounts attribute.

get_user_from_transactions(transaction_id): Retrieves the user associated with a given transaction ID from the Transactions table. Assumes the Transactions model has a sender attribute.

get_user_from_account_number(account_number): Retrieves the user associated with a given account number from the Accounts table. Assumes the Accounts model has a user attribute.

### TransactionServices

Class Attributes:

\_\_db: An instance of the DB class, initialized when a TransactionService instance is created.

reload(): Reloads the \_\_db instance, which may be involved in managing database connections or configurations.

Methods:

\*\*create_transaction(kwargs): Creates a new transaction. Takes keyword arguments like sender_id, receiver_id, and amount. Creates a Transactions model instance, sets its attributes, adds it to the database, and saves the changes.

get_transaction(transaction_id): Retrieves a specific transaction from the database based on transaction_id.

view_user_specific_transactions(user_id): Retrieves all transactions where the given user_id matches the sender_id. Fetches a list of transactions from the database.

### Messages

MessagesService

Class Attributes:

\_\_db: An instance of the DB class.

reload(): Reloads the \_\_db instance, which may be involved in managing database configurations.

Methods:

\*\*create_message(self, kwargs): Creates a new message. Takes keyword arguments like content, sender_id, and receiver_id. Adds the message to the database and saves the changes. Returns the created message.

get_message(self, message_id): Retrieves a message based on message_id.

get_specific_user_messages(self, user_id): Retrieves all messages associated with a specific user identified by user_id.

delete_message(self, message_id): Deletes a message based on message_id.

delete_all_user_messages(self, user_id): Deletes all messages associated with a specific user identified by user_id.

### TransactionLogic

TransactionService

Class Attributes:

\_\_db: An instance of the DB class, representing a database connection.

reload(): Reloads the \_\_db instance during initialization.

Methods:

\*\*create_transaction(self, kwargs): Creates a new transaction. Takes keyword arguments like sender_id, receiver_id, and amount. Adds the transaction to the database and saves the changes. Returns the created transaction.

get_transaction(self, transaction_id): Retrieves a transaction from the database based on transaction_id.

view_user_specific_transactions(self, user_id): Retrieves all transactions where the specified user is the sender, identified by user_id.

### UserAccount

AccountService

Class Attributes:

\_\_db: An instance of the DB class, representing a database connection.

reload(): Reloads the \_\_db instance during initialization.

Methods:

create_account_number(self): Generates a random account number.

\*\*create_account(self, kwargs): Creates a new account. Generates a unique account number, checks for its existence, creates an Accounts model instance, adds it to the database, and saves the changes.

get_account(self, account_number): Retrieves an account from the database based on account_number.

add_total_funds(self, account_number, amount): Adds funds to an account's total balance.

transact(self, amount, sender_id, receiver_id): Performs a transaction. Subtracts the specified amount from the sender's account and adds it to the receiver's account. Includes error checking, such as ensuring the amount is greater than 100, checking for valid IDs, verifying sufficient funds, and handling transactions with SQL transactions (\_db.begin(), \_db.rollback(), and \_db.save()).
