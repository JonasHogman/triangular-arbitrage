from datetime import datetime
import tools.pairs
from decimal import *
import tools.db
import rethinkdb as r
import logging
import time
from influxdb import InfluxDBClient

module_logger = logging.getLogger('arbitrage')


def test_calculation(btc_eth, eth_zec, btc_zec, fee, btc_starting_amount, eth_starting_amount, zec_starting_amount):
    btc_eth_ask_price = Decimal(btc_eth['ask'][0])
    btc_eth_bid_price = Decimal(btc_eth['bid'][0])
    eth_zec_ask_price = Decimal(eth_zec['ask'][0])
    eth_zec_bid_price = Decimal(eth_zec['bid'][0])
    btc_zec_ask_price = Decimal(btc_zec['ask'][0])
    btc_zec_bid_price = Decimal(btc_zec['bid'][0])

    btc_eth_ask_amount = Decimal(btc_eth['ask'][1])
    btc_eth_bid_amount = Decimal(btc_eth['bid'][1])
    eth_zec_ask_amount = Decimal(eth_zec['ask'][1])
    eth_zec_bid_amount = Decimal(eth_zec['bid'][1])
    btc_zec_ask_amount = Decimal(btc_zec['ask'][1])
    btc_zec_bid_amount = Decimal(btc_zec['bid'][1])

    startBTC_BTCETH_r1 = (btc_eth_ask_price * btc_eth_ask_amount).quantize(Decimal('.00000001'),
                                                                           rounding=ROUND_HALF_UP)

    startBTC_ETHZEC_r1 = ((eth_zec_ask_price * eth_zec_ask_amount).quantize(Decimal('.00000001'),
                                                                            rounding=ROUND_HALF_UP) * btc_eth_ask_price).quantize(
        Decimal('.00000001'), rounding=ROUND_HALF_UP)

    startBTC_BTCZEC_r1 = ((btc_zec_bid_amount * eth_zec_ask_price).quantize(Decimal('.00000001'),
                                                                            rounding=ROUND_HALF_UP) * btc_eth_ask_price).quantize(
        Decimal('.00000001'), rounding=ROUND_HALF_UP)

    start_BTC_r1 = min(startBTC_BTCETH_r1, startBTC_ETHZEC_r1, startBTC_BTCZEC_r1).quantize(Decimal('.00000001'),
                                                                                            rounding=ROUND_HALF_UP)

    # print(startBTC_BTCETH_r1, startBTC_ETHZEC_r1, startBTC_BTCZEC_r1)

    trade_1_r1 = (start_BTC_r1 / btc_eth_ask_price).quantize(Decimal('.00000001'), rounding=ROUND_HALF_UP)
    trade_2_r1 = (trade_1_r1 / eth_zec_ask_price).quantize(Decimal('.00000001'), rounding=ROUND_HALF_UP)
    trade_3_r1 = (trade_2_r1 * btc_zec_bid_price).quantize(Decimal('.00000001'), rounding=ROUND_HALF_UP)

    # print('Trading', start_BTC_r1, 'BTC for', trade_1_r1, 'ETH')
    # print('Trading', trade_1_r1, 'ETH for', trade_2_r1, 'ZEC')
    # print('Trading', trade_2_r1, 'ZEC for', trade_3_r1, 'BTC')
    #
    # print(f'Round 1 profit in BTC: {trade_3_r1 - start_BTC_r1:.8f}')
    # print(f'Round 1 profit in percentage: {((trade_3_r1 / start_BTC_r1) - 1) * 100:.6f}%')

    startBTC_BTCZEC_r2 = (btc_zec_ask_price * btc_zec_ask_amount).quantize(Decimal('.00000001'),
                                                                           rounding=ROUND_HALF_UP)
    startBTC_ETHZEC_r2 = (eth_zec_bid_amount.quantize(Decimal('.00000001'),
                                                      rounding=ROUND_HALF_UP) * btc_zec_ask_price).quantize(
        Decimal('.00000001'), rounding=ROUND_HALF_UP)
    startBTC_BTCETH_r2 = (btc_eth_bid_amount / eth_zec_bid_price.quantize(Decimal('.00000001'),
                                                                          rounding=ROUND_HALF_UP) * btc_zec_ask_price).quantize(
        Decimal('.00000001'), rounding=ROUND_HALF_UP)

    start_BTC_r2 = min(startBTC_BTCETH_r2, startBTC_ETHZEC_r2, startBTC_BTCZEC_r2).quantize(Decimal('.00000001'),
                                                                                            rounding=ROUND_HALF_UP)

    trade_1_r2 = (start_BTC_r2 / btc_zec_ask_price).quantize(Decimal('.00000001'), rounding=ROUND_HALF_UP)
    trade_2_r2 = (trade_1_r2 * eth_zec_bid_price).quantize(Decimal('.00000001'), rounding=ROUND_HALF_UP)
    trade_3_r2 = (trade_2_r2 * btc_eth_bid_price).quantize(Decimal('.00000001'), rounding=ROUND_HALF_UP)

    # print(startBTC_BTCZEC_r2, startBTC_ETHZEC_r2, startBTC_BTCETH_r2)

    # print('Trading', start_BTC_r2, 'BTC for', trade_1_r2, 'ETH')
    # print('Trading', trade_1_r2, 'ETH for', trade_2_r2, 'ZEC')
    # print('Trading', trade_2_r2, 'ZEC for', trade_3_r2, 'BTC')
    #
    # print(f'Round 2 profit in BTC: {trade_3_r2 - start_BTC_r2:.8f}')
    # print(f'Round 2 profit in percentage: {((trade_3_r2 / start_BTC_r2) - 1) * 100:.6f}%')

    return ((trade_3_r1 / start_BTC_r1) - 1) * 100, ((trade_3_r2 / start_BTC_r2) - 1) * 100


def calculate_triangle_both_ways(base_secondary, secondary_token, base_token, base, secondary, token, fee):
    # first path
    # TODO: Step one should use multiplication of price*amount, not 1/
    step_1 = round((1 / base_secondary['ask'][0]) * Decimal(1 - fee), 8)  # buy secondary with base
    step_2 = round((step_1 / secondary_token['ask'][0]) * Decimal(1 - fee), 8)  # buy token with secondary
    step_3 = round((step_2 * base_token['bid'][0]) * Decimal(1 - fee), 8)  # sell tokens for base

    # second path
    step_4 = round((1 / base_token['ask'][0]) * Decimal(1 - fee), 8)  # buy token with base
    step_5 = round((step_4 * secondary_token['bid'][0]) * Decimal(1 - fee), 8)  # buy secondary with token
    step_6 = round((step_5 * base_secondary['bid'][0]) * Decimal(1 - fee), 8)  # buy base with secondary

    max_profit = max(float((step_3 - 1) * 100), float((step_6 - 1) * 100))

    print(float((step_3 - 1) * 100), float((step_6 - 1) * 100))

    # conn = tools.db.get_connection()

    # try:
    #     previous_max_profit = \
    #         r.db('arbitrage').table('{}_{}_{}'.format(base, secondary, token)).order_by(
    #             index=r.desc('timestamp')).limit(1).nth(0).run(
    #             conn)['profit']
    #
    # except r.ReqlNonExistenceError as e:
    #     previous_max_profit = 0

    # amounts_to_trade = calculate_lowest_amount(base_secondary, secondary_token, base_token, 1)

    if max(float((step_3 - 1) * 100), float((step_6 - 1) * 100)) > 0:
        print(datetime.now(), max(float((step_3 - 1) * 100), float((step_6 - 1) * 100)), base, secondary, token)

    # if max_profit != previous_max_profit:
    #     r.db('arbitrage').table('{}_{}_{}'.format(base, secondary, token)).insert({
    #         "timestamp": r.now(),
    #         "combination": '{}_{}_{}'.format(base, secondary, token),
    #         "profit": max(float((step_3 - 1) * 100), float((step_6 - 1) * 100))
    #     }).run(conn)

    else:
        pass

    return max_profit


def run_orderbook(orderbook, pair):
    module_logger.debug('%s - %s', orderbook, pair)
    """
    Calculate new profit for each affected triangular combination
    :param orderbook:
    :param pair: last updated pair
    :return:
    """
    streamable_updates = {}
    conn = tools.db.get_influx_connection()
    for item in tools.pairs.get_checkable_combinations(tools.pairs.triangular_pair_list(), pair.split('-')[1],
                                                       pair.split('-')[0]):
        try:
            triangular_combination = "{}_{}_{}".format(item[0], item[1], item[2])
            base_secondary = orderbook["{}-{}".format(item[1], item[0])]
            secondary_token = orderbook["{}-{}".format(item[2], item[1])]
            base_token = orderbook["{}-{}".format(item[2], item[0])]

            streamable_updates[triangular_combination] = test_calculation(
                base_secondary,
                secondary_token,
                base_token,
                0, 1000, 1000, 1000)

            db_entry = [
                {
                    "measurement": "arbitrage",
                    "tags": {
                        "triangle": triangular_combination,
                    },
                    "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "fields": {
                        "route1": float(streamable_updates[triangular_combination][0]),
                        "route2": float(streamable_updates[triangular_combination][1])

                    }
                }
            ]

            conn.write_points(db_entry)

            # if streamable_updates["{}_{}_{}".format(item[0], item[1], item[2])] > 0:
            #     pass
            # calculate_lowest_amount(base_secondary, secondary_token, base_token)

        # pass if all pairs haven't been initialized yet
        except KeyError as e:
            pass

    return streamable_updates


# (pair, amount)
# example: {'bid': (Decimal('3560.50421070'), Decimal('2.26178747')), 'ask': (Decimal('3563.24371488'), Decimal('0.73040534'))} {'bid': (Decimal('0.00057731'), Decimal('386.87242321')), 'ask': (Decimal('0.00058088'), Decimal('125.49542822'))} {'bid': (Decimal('3560.50421070'), Decimal('2.26178747')), 'ask': (Decimal('3563.24371488'), Decimal('0.73040534'))}
def calculate_lowest_amount(base_secondary, secondary_token, base_token, path, fee):
    """
    :param base_secondary:
    :param secondary_token:
    :param base_token:
    :return:
    """
    module_logger.info('Input calculate_lowest_amount: %s - %s - %s', base_secondary, secondary_token, base_token)

    if path == 1:
        base_secondary_amount = round(base_secondary['ask'][1] * base_secondary['ask'][0], 8)
        secondary_token_amount = round(secondary_token['ask'][1] * base_token['bid'][0] * Decimal(1 - fee), 8)
        base_token_amount = round(base_token['bid'][1] * base_token['bid'][0], 8)

        max_base_amount = min(base_secondary_amount, secondary_token_amount, base_token_amount)

    elif path == 2:
        base_secondary_amount = round(base_secondary['bid'][1] * base_secondary['bid'][0], 8)
        secondary_token_amount = round(secondary_token['ask'][1] * base_secondary['bid'][0] * Decimal(1 - fee), 8)
        base_token_amount = round(base_token['ask'][1] * base_token['ask'][0], 8)

        max_base_amount = min(base_secondary_amount, secondary_token_amount, base_token_amount)

    module_logger.info('Input calculate_lowest_amount: %s - %s - %s', base_secondary_amount,
                       secondary_token_amount, base_token_amount)

    print(datetime.now(), ': Lowest amounts for USDT-BTC, BTC-ETH, USDT-ETH:', base_secondary_amount,
          secondary_token_amount, base_token_amount)

    return max_base_amount
