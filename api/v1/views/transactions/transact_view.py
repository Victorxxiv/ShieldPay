from api.v1.views.transactions import user_trans
from flask import jsonify, request
from flask_jwt_extended import jwt_required
from utils.user_account import AccountService
from utils.TransactionServices import TransactionServices
from auth.auth import Authentication


# Intialize services
account_service = AccountService()
transaction_service = TransactionServices()
user_authenticator = Authentication()

# Create transaction
@user_trans.route('/transact', methods=['POST'], endpoint='create_transaction')
@jwt_required()
def create_transaction():
    # Get authenticated user
    sender_id = user_authenticator.get_authenticated_user()
    account_number = request.json.get('account_number')
    receiver_id = account_service.get_user_id_from_account_number(account_number)
    amount = request.json.get('amount')
    if not account_number:
        return jsonify({'message': 'account_number is required'}), 400
    if not amount:
        return jsonify({'message': 'amount is required'}), 400
    if not receiver_id:
        return jsonify({'message': 'there was an error with the account number'}), 400
    if not sender_id:
        return jsonify({'message': 'sender_id is required'}), 400
    if sender_id == receiver_id:
        return jsonify({'message': 'you cannot send money to yourself'}), 400
    account_service.transact(amount, sender_id, receiver_id)
    transaction = transaction_service.create_transaction(sender_id=sender_id, receiver_id=receiver_id, amount=amount)
    return jsonify({'message': 'transaction created successfully', 'transaction': transaction.serialize()}), 201


# Get all transactions
@user_trans.route('/transactions', methods=['GET'], endpoint='get_all_transactions')
@jwt_required()
def get_all_transactions():
    # Get authenticated user
    user_id = user_authenticator.get_authenticated_user()
    transactions = transaction_service.get_all_transactions(user_id)
    return jsonify(transactions), 200


# Get a specific transaction
@user_trans.route('/transaction/<int:transaction_id>', methods=['GET'], endpoint='get_transaction')
@jwt_required()
def get_transaction(transaction_id):
    transaction = transaction_service.get_transaction(transaction_id)
    if not transaction:
        return jsonify({'message': 'transaction not found'}), 404
    return jsonify({'message': 'transaction found', 'transaction': transaction.serialize()}), 200


# Approve a transaction
@user_trans.route('/approve/<string:transaction_id>', methods=['PATCH'], endpoint='approve_transaction')
@jwt_required()
def approve_transaction(transaction_id):
    transaction = transaction_service.get_transaction(transaction_id)
    if not transaction:
        return jsonify({'message': 'transaction not found'}), 404

    if transaction.status == 'pending':
        # getting sender and receiver details from the transaction id
        sender_id = transaction.sender_id
        receiver_id = transaction.receiver_id
        amount = transaction.amount
        account_service.send_money(amount, sender_id, receiver_id)
        transaction_service.approve_transaction(transaction_id)
        return jsonify({'message': 'transaction approved'}), 200


# Cancel a transaction
@user_trans.route('/cancel/<string:transaction_id>', methods=['PATCH'], endpoint='cancel_transaction')
@jwt_required()
def cancel_transaction(transaction_id):
    transaction = transaction_service.get_transaction(transaction_id)
    if not transaction:
        return jsonify({'message': 'transaction not found'}), 404
    if transaction.status == "pending":
        account_service.create_conflict(transaction_id)
        return jsonify({'message': 'transaction cancelled'}), 200


# Deposit funds
@user_trans.route('/deposit', methods=['POST'], endpoint='deposit_funds')
@jwt_required()
def deposit_funds():
    pass

@user_trans.route('/withdraw', methods=['POST'], endpoint='withdraw_funds')
@jwt_required()
def withdraw_funds():
    pass