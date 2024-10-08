from models.basemodel import BaseModel, Base
from sqlalchemy import Column, String, ForeignKey, Float
from sqlalchemy.orm import relationship

class Transactions(BaseModel, Base):

    __tablename__ = 'transactions'

    # Define the foreign key relationship to the sender user
    sender_id = Column(String(255), ForeignKey('users.id'), nullable=False)

    # Define the foreign key relationship to the receiver user
    receiver_id = Column(String(255), ForeignKey('users.id'), nullable=False)

    # Amount of the transaction
    amount = Column(Float, nullable=False)

    # transaction status
    status = Column(String(255), nullable=False, default='pending')

    conflict = Column(String(255), nullable=False, default='False')
    # Define the sender and receiver relationships

    sender = relationship('User', foreign_keys=[sender_id], back_populates='sent_transactions')
    receiver = relationship('User', foreign_keys=[receiver_id], back_populates='received_transactions')
