from typing import Dict, List
from polaris.integrations import SEP31Receiver
from polaris.models import Asset
from rest_framework.request import Request

from polaris.sep10.token import SEP10Token
from polaris.models import Transaction
from .users import user_for_id, verify_bank_account

class AnchorCrossBorderPayment(SEP31Receiver):
    def info(
        request: Request,
        asset: Asset,
        lang: str,
        *args: Dict,
        **kwargs: List
    ):
        return {
            "sep12": {
                "sender": {
                    "types": {
                        "sep31-sender": {
                            "description": "the basic type for sending customers"
                        }
                    }
                },
                "receiver": {
                    "types": {
                        "sep31-receiver": {
                            "description": "the basic type for receiving customers"
                        }
                    }
                },
            },
            "fields": {
                "transaction": {
                    "routing_number": {
                        "description": "routing number of the destination bank account"
                    },
                    "account_number": {
                        "description": "bank account number of the destination"
                    },
                },
            },
        }
    
    def process_post_request(
        self,
        token: SEP10Token,
        request: Request,
        params: Dict,
        transaction: Transaction,
        *args: List,
        **kwargs: Dict,
    ):
        sending_user = user_for_id(params.get("sender_id"))
        receiving_user = user_for_id(params.get("receiver_id"))
        if not sending_user or not sending_user.kyc_approved:
            return {"error": "customer_info_needed", "type": "sep31-sender"}
        if not receiving_user or not receiving_user.kyc_approved:
            return {"error": "customer_info_needed", "type": "sep31-receiver"}
        transaction_fields = params.get("fields", {}).get("transaction")
        if not transaction_fields:
            return {
                "error": "transaction_info_needed",
                "fields": {
                    "transaction": {
                        "routing_number": {
                            "description": "routing number of the destination bank account"
                        },
                        "account_number": {
                            "description": "bank account number of the destination"
                        },
                    }
                }
            }
        try:
            verify_bank_account(
                transaction_fields.get("routing_number"),
                transaction_fields.get("account_number")
            )
        except ValueError:
            return {"error": "invalid routing or account number"}
        sending_user.add_transaction(transaction)
        receiving_user.add_transaction(transaction)

