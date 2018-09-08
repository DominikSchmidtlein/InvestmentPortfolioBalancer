from balancer.configmanager import ConfigManager
from balancer import composition
from balancer import questrade
from balancer import questradewrapper
from balancer import calculator
from balancer.tablegenerator import TableGenerator
from balancer import email

def lambda_handler(event, context):
    # retrieve config
    configmanager = ConfigManager()
    config = configmanager.get_config()
    # connect to questrade
    qclient = questrade.Client(config['refresh_token'], config['account_id'])
    # update config
    config.update(qclient.login_response)
    configmanager.put_config(config)
    # retrieve desired composition
    comp = composition.retrieve(int(config['account_id']))
    assert sum(v['composition'] for v in comp.values()) - 1 <= 0.00000001
    # get portfolio positions
    positions = qclient.get_positions(
        ['currentPrice', 'openQuantity', 'currentMarketValue', 'averageEntryPrice'])
    # get portfolio balances
    wrapper = questradewrapper.ClientWrapper(qclient)
    balances = wrapper.balances()
    # calculate balanced portfolio
    purchases, new_balances = calculator.balance(positions, balances, comp, price_getter(qclient))
    # generate tables
    tablegenerator = TableGenerator()
    p_table = tablegenerator.transactions_table(purchases)
    b_table = tablegenerator.balances_table(new_balances)

    # email tables
    email.send_email("Questrade Portfolio Overview", str(p_table) + "\n\n" + str(b_table))

    # print tables
    print(p_table)
    print(b_table)

def price_getter(qclient):
    def get_price(symbol):
        symbol_id = qclient.get_symbol(symbol, ['symbolId'])['symbolId']
        current_price = qclient.get_quote(symbol_id, ['lastTradePrice'])['lastTradePrice']
    return get_price

if __name__ == '__main__':
    lambda_handler(None, None)
