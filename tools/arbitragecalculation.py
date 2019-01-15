from datetime import datetime
import tools.pairs
from decimal import *
import tools.db
import rethinkdb as r


def calculate_triangle_both_ways(base_by_secondary, secondary_by_token, base_by_token, base, secondary, token):
    # first path
    step_1 = round((1 / base_by_secondary['ask'][0]) * Decimal(1 - 0.002), 8)  # buy secondary with base
    step_2 = round((step_1 / secondary_by_token['ask'][0]) * Decimal(1 - 0.002), 8)  # buy token with secondary
    step_3 = round((step_2 * base_by_token['bid'][0]) * Decimal(1 - 0.002), 8)  # sell tokens for base

    # second path
    step_4 = round((1 / base_by_token['ask'][0]) * Decimal(1 - 0.002), 8)  # buy token with base
    step_5 = round((step_4 * secondary_by_token['bid'][0]) * Decimal(1 - 0.002), 8)  # buy secondary with token
    step_6 = round((step_5 * base_by_secondary['bid'][0]) * Decimal(1 - 0.002), 8)  # buy base with secondary

    max_profit = max(float((step_3 - 1) * 100), float((step_6 - 1) * 100))

    conn = tools.db.get_connection()

    try:
        previous_max_profit = \
            r.db('arbitrage').table('{}_{}_{}'.format(base, secondary, token)).order_by(
                index=r.desc('timestamp')).limit(1).nth(0).run(
                conn)['profit']

    except r.ReqlNonExistenceError as e:
        previous_max_profit = 0

    if max_profit != previous_max_profit:
        r.db('arbitrage').table('{}_{}_{}'.format(base, secondary, token)).insert({
            "timestamp": r.now(),
            "combination": '{}_{}_{}'.format(base, secondary, token),
            "profit": max(float((step_3 - 1) * 100), float((step_6 - 1) * 100))
        }).run(conn)

    if max(float((step_3 - 1) * 100), float((step_6 - 1) * 100)) > 0:
        print(datetime.now(), max(float((step_3 - 1) * 100), float((step_6 - 1) * 100)), base, secondary, token)

    else:
        pass

    return max_profit


def run_orderbook(orderbook, pair):
    """
    Calculate new profit for each affected triangular combination
    :param orderbook:
    :param pair: last updated pair
    :return:
    """
    streamable_updates = {}
    for item in tools.pairs.get_checkable_combinations(tools.pairs.triangular_pair_list(), pair.split('-')[1],
                                                       pair.split('-')[0]):
        try:
            streamable_updates["{}_{}_{}".format(item[0], item[1], item[2])] = calculate_triangle_both_ways(
                orderbook["{}-{}".format(item[1], item[0])],
                orderbook["{}-{}".format(item[2], item[1])],
                orderbook["{}-{}".format(item[2], item[0])], item[0], item[1], item[2])

        except KeyError as e:
            pass

    return streamable_updates
