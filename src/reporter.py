from collections import defaultdict
from datetime import datetime
from src.api import LevelMoneyApiClient


class TransactionReporter(object):
    TRANSACTION_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

    def __init__(self, api_client_credentials):
        self.api_client = LevelMoneyApiClient(**api_client_credentials)

    def predict_the_future(self):
        today = datetime.today()
        this_year = today.year
        this_month = today.month
        projected_transaction = self.api_client.get_projected_transactions(year=this_year, month=this_month)
        return projected_transaction

    def get_all_user_transactions(self):
        return self.api_client.get_all_transactions()

    def calculate_user_monthly_costs(self, all_user_transactions, filter_rules, ignore_cc_payments):
        all_transactions_by_date = defaultdict(list)

        if ignore_cc_payments:
            # merge in case other filtering rules like ignore-donuts are active
            merchant_filter_rules = filter_rules.get('raw-merchant', [])
            payment_merchants = ['CC Payment', 'Credit Card Payment']
            merchant_filter_rules.extend(payment_merchants)

            filter_rules['raw-merchant'] = merchant_filter_rules

        for transaction in all_user_transactions:
            # inject filtering rules
            for rule_name, rule_value in filter_rules.items():
                if isinstance(rule_value, list) and transaction.get(rule_name) in rule_value:
                    continue

                if isinstance(rule_value, str) and transaction.get(rule_value) == rule_value:
                    continue

            transaction_date = transaction['transaction-time']
            all_transactions_by_date[transaction_date].append(transaction['amount'])

        # income: transaction amount > 0
        # spent: transaction amount < 0
        # total = income + spent
        # average: monthly average (total / 2)
        formatted_transactions_by_date = dict()

        for transaction_date, transaction_amounts in all_transactions_by_date.items():
            if transaction_date not in formatted_transactions_by_date:
                formatted_transactions_by_date[transaction_date] = dict(income=list(), spent=list())

            total = 0
            for transaction_amount in transaction_amounts:
                if transaction_amount > 0:
                    formatted_transactions_by_date[transaction_date]['income'].append(transaction_amount)

                if transaction_amount < 0:
                    formatted_transactions_by_date[transaction_date]['spent'].append(transaction_amount)

                total += transaction_amount

            formatted_transactions_by_date[transaction_date]['credit_type'] = 'credit' if total >= 0 else 'debit'
            formatted_transactions_by_date[transaction_date]['total'] = float(total/1000)
            formatted_transactions_by_date[transaction_date]['average'] = formatted_transactions_by_date[transaction_date]['total'] / 2
            formatted_transactions_by_date[transaction_date]['total_spent'] = sum(formatted_transactions_by_date[transaction_date]['spent'])
            formatted_transactions_by_date[transaction_date]['total_income'] = sum(formatted_transactions_by_date[transaction_date]['income'])

        if ignore_cc_payments:
            now = datetime.now()
            one_day_in_seconds = 86400

            for transaction_date, formatted_transactions in formatted_transactions_by_date.items():
                # transactions occurred in the past 24hrs
                formatted_transaction_time = datetime.strptime(transaction_date, self.TRANSACTION_DATE_FORMAT)

                if (now - formatted_transaction_time).total_seconds() <= one_day_in_seconds:
                    # flip to positive amounts to find a match
                    spent_transactions = set([amount * -1 for amount in formatted_transactions['spent']])

                    cc_payments = set(formatted_transactions['income']) & spent_transactions

                    if len(cc_payments) > 0:
                        # filter out cc payments, with an in-place remove
                        for cc_payment in cc_payments:
                            formatted_transactions['income'].remove(cc_payment)
                            formatted_transactions['spent'].remove(cc_payment * -1)

        return formatted_transactions_by_date
