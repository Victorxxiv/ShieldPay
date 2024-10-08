from models.transactions import Transactions
from db.storage import DB

#  Class for Transaction Services
class TransactionService:
    __db = DB()
    __db.reload()

    def create_transaction(self, **kwargs):
        """Create transaction"""
        sender_id = kwargs.get('sender_id')
        receiver_id = kwargs.get('receiver_id')
        amount = kwargs.get('amount')
        transaction = Transactions(sender_id=sender_id, receiver_id=receiver_id, amount=amount)
        self.__db.add(transaction)
        self.__db.save()
        return transaction

    def get_transaction(self, transaction_id):
        """Get transaction"""
        transaction = self.__db.query(Transactions).filter_by(id=transaction_id).first()
        return transaction

    def view_user_specific_transactions(self, user_id):
        """View user specific transactions"""
        transactions = self.__db.query(Transactions).filter_by(sender_id=user_id).all()
        return transactions

    def approve_transaction(self, transaction_id):
        """Approve transaction"""
        transaction = self.get_transaction(transaction_id)
        transaction.status = 'approved'
        self.__db.save()

    def decline_transaction(self, transaction_id):
        """Decline transaction"""
        transaction = self.get_transaction(transaction_id)
        transaction.status = 'declined'
        self.__db.save()

    def get_all_transactions(self, user_id):
        """Get all transactions"""
        transactions = self.__db.query(Transactions).filter_by(sender_id=user_id).all()
        return transactions
