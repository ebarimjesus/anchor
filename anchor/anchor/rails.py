from typing import List, Dict
from django.db.models import QuerySet
from polaris.models import Transaction
from polaris.integrations import RailsIntegration
from .rails import (
    get_reference_id,
    has_received_payment,
    submit_payment,
    get_payment,
    PaymentStatus,
    calculate_fee,
    initiate_refund,
    is_valid_payment_amount
)

class AnchorRails(RailsIntegration):
    def poll_pending_deposits(
        self,
        pending_deposits: QuerySet,
        *args: List,
        **kwargs: Dict
    ):
        received_payments = []
        for transaction in pending_deposits:
            if has_received_payment(get_reference_id(transaction)):
                received_payments.append(transaction)
        return received_payments
    
    def execute_outgoing_transaction(
        self,
        transaction: Transaction,
        *args: List,
        **kwargs: Dict
    ):
        if transaction.amount_in != transaction.amount_expected:
            if not is_valid_payment_amount(transaction.amount_in):
                initiate_refund(transaction)
                transaction.refunded = True
                transaction.status = Transaction.STATUS.error
                transaction.status_message = "the amount received is not valid, refunding."
                transaction.save()
                return
            transaction.amount_fee = calculate_fee(transaction)
            transaction.amount_out = round(
                transaction.amount_in - transaction.amount_fee,
                transaction.asset.significant_decimals
            )
            transaction.save()
        payment = submit_payment(transaction)
        if payment.status == PaymentStatus.DELIVERED:
            transaction.status = Transaction.STATUS.completed
        elif payment.status == PaymentStatus.INITIATED:
            transaction.status = Transaction.STATUS.pending_external
        else:  # payment.status == PaymentStatus.FAILED:
            transaction.status = Transction.STATUS.error
            transaction.status_message = "payment failed, contact customer support."
        transaction.external_transaction_id = payment.id
        transaction.save()

    def poll_outgoing_transactions(
        self,
        transactions: QuerySet,
        *args: List,
        **kwargs: Dict
    ) -> List[Transaction]:
        delivered_transactions = []
        for transaction in transactions:
            payment = get_payment(transaction)
            if payment.status == PaymentStatus.INITIATED:
                continue
            if payment.status == PaymentStatus.FAILED:
                transaction.status = Transction.STATUS.error
                transaction.status_message = "payment failed, contact customer support."
                transaction.save()
                continue
            delivered_transactions.append(transaction)
        return delivered_transactions
    

