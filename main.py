from __future__ import division
try:
    from ConfigParser import SafeConfigParser as ConfigParser
except ImportError:
    from configparser import ConfigParser
from src.reporter import TransactionReporter

import argparse
import logging
import json


def read_credential_config():
    credential_file = 'credential.ini'
    parser = ConfigParser()
    parser.read(credential_file)

    api_client_credential = dict()
    api_client_credential['interview_token'] = parser.get('level_money', 'interview_token')
    api_client_credential['api_token'] = parser.get('level_money', 'api_token')
    api_client_credential['uid'] = parser.getint('level_money', 'uid')

    return api_client_credential


def main(cli_args):
    logging.info('Loads a user\'s transactions from the GetAllTransactions endpoint')

    config_payload = read_credential_config()
    transaction_reporter = TransactionReporter(config_payload)
    all_user_transactions = transaction_reporter.get_all_user_transactions()

    if cli_args.crystal_ball:
        projected_this_month_transactions = transaction_reporter.predict_the_future()
        # merge into all transactions
        all_user_transactions.extend(projected_this_month_transactions)

    logging.info('Determines how much money the user spends and makes in each of the months for which we have data, '
                 'and in the "average" month. What "average" means is up to you.')

    # set of filtering rules to exclude matched transactions
    filtering_rules = dict()
    filtering_rules['is-pending'] = False

    if cli_args.ignore_donuts:
        donut_shops = ['Krispy Kreme Donuts', 'DUNKIN #336784']
        filtering_rules['raw-merchant'] = donut_shops

    monthly_costs = transaction_reporter.calculate_user_monthly_costs(all_user_transactions,
                                                                      filtering_rules,
                                                                      ignore_cc_payments=cli_args.ignore_cc_payments)
    print(json.dumps(monthly_costs, indent=4, sort_keys=True))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description='CapitalOne coding exercise')
    parser.add_argument('--ignore-donuts', '-id', action='store_true', help='filter out donut-related transactions (are you serious!?)')
    parser.add_argument('--crystal-ball', '-cb', action='store_true', help='Merge this month\'s projected transactions')
    parser.add_argument('--ignore-cc-payments', '-ic', action='store_true', help='ignore cc payments')

    cli_args = parser.parse_args()

    main(cli_args)
