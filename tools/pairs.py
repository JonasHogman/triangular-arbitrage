import requests
import json


def get_bid_ask():
    """
    Creates a dictionary of highest bid and lowest ask values for all trading pairs available on the exchange,
    used for getting all the trading pairs
    """
    bid_ask_dict = {}
    orig_dict = json.loads(requests.get('https://poloniex.com/public?command=returnTicker'))
    for key, value in orig_dict.items():
        bid_ask_dict[str(key)] = {'ask': float(value['lowestAsk']), 'bid': float(value['highestBid'])}

    return bid_ask_dict


# figure out what this does
def get_base_list(curr_dict):
    """
    Retrieves the base currency for a triangular trade
    """
    curr_list = []
    for key in curr_dict.keys():
        base_curr = key.split('_')[0]
        if base_curr not in curr_list:
            curr_list.append(base_curr)
    return curr_list


# takes an input of a combination of all
def create_combination_dict(btc_list, eth_list, xmr_list, usdt_list):
    all_list = [btc_list, eth_list, xmr_list, usdt_list]
    tri_list = []

    for item in get_curr_in_common(btc_list, eth_list):
        tri_list.append(['BTC', 'ETH', item])
        # tri_list.append(['ETH', 'BTC', item])

    for item in get_curr_in_common(btc_list, xmr_list):
        tri_list.append(['BTC', 'XMR', item])
    #        tri_list.append(['XMR', 'BTC', item])

    for item in get_curr_in_common(btc_list, usdt_list):
        # tri_list.append(['BTC', 'USDT', item])
        tri_list.append(['USDT', 'BTC', item])

    #    for item in get_curr_in_common(eth_list, xmr_list):
    #        tri_list.append(['ETH', 'XMR', item])
    #        tri_list.append(['XMR', 'ETH', item])

    for item in get_curr_in_common(eth_list, usdt_list):
        # tri_list.append(['ETH', 'USDT', item])
        tri_list.append(['USDT', 'ETH', item])

    #    for item in get_curr_in_common(xmr_list, usdt_list):
    #        tri_list.append(['XMR', 'USDT', item])
    #        tri_list.append(['USDT', 'XMR', item])

    return tri_list


def get_curr_in_common(list1, list2):
    in_common = []
    for item in list1:
        if item in list2:
            in_common.append(item)
    return in_common


def create_combinations():
    ##curr_dict is a dictionary of all trading pairs and their prices
    curr_dict = get_bid_ask()

    btc_list = []
    eth_list = []
    xmr_list = []
    usdt_list = []

    # get all trading pairs that start with one of the four parent coins
    for key, value in curr_dict.items():
        if key.split('_')[0] == 'BTC':
            btc_list.append(key.split('_')[1])
        if key.split('_')[0] == 'ETH':
            eth_list.append(key.split('_')[1])
        if key.split('_')[0] == 'XMR':
            xmr_list.append(key.split('_')[1])
        if key.split('_')[0] == 'USDT':
            usdt_list.append(key.split('_')[1])

    # get all the triangular possibilities
    combinations = create_combination_dict(btc_list, eth_list, xmr_list, usdt_list)
    pairs = list(curr_dict.keys())
    pairs = [p.replace('_', '-') for p in pairs]

    return combinations, pairs


def triangular_pair_list():
    return [['BTC', 'ETH', 'LSK'], ['BTC', 'ETH', 'STEEM'], ['BTC', 'ETH', 'ETC'], ['BTC', 'ETH', 'REP'],
            ['BTC', 'ETH', 'ZEC'], ['BTC', 'ETH', 'GNT'], ['BTC', 'ETH', 'BCH'], ['BTC', 'ETH', 'ZRX'],
            ['BTC', 'ETH', 'CVC'], ['BTC', 'ETH', 'OMG'], ['BTC', 'ETH', 'GAS'], ['BTC', 'ETH', 'EOS'],
            ['BTC', 'ETH', 'SNT'], ['BTC', 'ETH', 'KNC'], ['BTC', 'ETH', 'BAT'], ['BTC', 'ETH', 'LOOM'],
            ['BTC', 'ETH', 'QTUM'], ['BTC', 'ETH', 'MANA'], ['BTC', 'ETH', 'BNT'], ['BTC', 'XMR', 'BCN'],
            ['BTC', 'XMR', 'DASH'], ['BTC', 'XMR', 'LTC'], ['BTC', 'XMR', 'MAID'], ['BTC', 'XMR', 'NXT'],
            ['BTC', 'XMR', 'ZEC'], ['USDT', 'BTC', 'DASH'], ['USDT', 'BTC', 'DOGE'], ['USDT', 'BTC', 'LTC'],
            ['USDT', 'BTC', 'NXT'], ['USDT', 'BTC', 'STR'], ['USDT', 'BTC', 'XMR'], ['USDT', 'BTC', 'XRP'],
            ['USDT', 'BTC', 'ETH'], ['USDT', 'BTC', 'SC'], ['USDT', 'BTC', 'LSK'], ['USDT', 'BTC', 'ETC'],
            ['USDT', 'BTC', 'REP'], ['USDT', 'BTC', 'ZEC'], ['USDT', 'BTC', 'GNT'], ['USDT', 'BTC', 'BCH'],
            ['USDT', 'BTC', 'ZRX'], ['USDT', 'BTC', 'EOS'], ['USDT', 'BTC', 'SNT'], ['USDT', 'BTC', 'KNC'],
            ['USDT', 'BTC', 'BAT'], ['USDT', 'BTC', 'LOOM'], ['USDT', 'BTC', 'QTUM'], ['USDT', 'BTC', 'MANA'],
            ['USDT', 'BTC', 'BNT'], ['USDT', 'ETH', 'LSK'], ['USDT', 'ETH', 'ETC'], ['USDT', 'ETH', 'REP'],
            ['USDT', 'ETH', 'ZEC'], ['USDT', 'ETH', 'GNT'], ['USDT', 'ETH', 'BCH'], ['USDT', 'ETH', 'ZRX'],
            ['USDT', 'ETH', 'EOS'], ['USDT', 'ETH', 'SNT'], ['USDT', 'ETH', 'KNC'], ['USDT', 'ETH', 'BAT'],
            ['USDT', 'ETH', 'LOOM'], ['USDT', 'ETH', 'QTUM'], ['USDT', 'ETH', 'MANA'], ['USDT', 'ETH', 'BNT']]


def get_checkable_combinations(triangular_pair_list, base, secondary):
    checkable_list = []
    for item in triangular_pair_list:
        if base in item and secondary in item:
            checkable_list.append(item)
        else:
            pass
    return checkable_list


def gen_pairs():
    ret = {}
    pairs = requests.get('https://poloniex.com/public?command=returnTicker').json()
    for pair in pairs:
        if pairs[pair]['isFrozen'] == "0":
            ret[pairs[pair]['id']] = pair
        else:
            pass
    return ret


poloniex_id_pair_mapping = gen_pairs()
poloniex_pair_id_mapping = {value: key for key, value in poloniex_id_pair_mapping.items()}
poloniex_pair_mapping = {value.split("_")[1] + "-" + value.split("_")[0]: value for _, value in
                         poloniex_id_pair_mapping.items()}
