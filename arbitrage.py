from cryptofeed.callback import BookCallback
from cryptofeed import FeedHandler
from cryptofeed.exchanges import Poloniex
from cryptofeed.defines import L2_BOOK, BID, ASK
from tools.pairs import poloniex_pair_mapping
from tools.arbitragecalculation import run_orderbook
from sortedcontainers import SortedDict
import tools.db
import rethinkdb as r
import logging
import logging.config

# Examples of some handlers for different updates. These currently don't do much.
# Handlers should conform to the patterns/signatures in callback.py
# Handlers can be normal methods/functions or async. The feedhandler is paused
# while the callbacks are being handled (unless they in turn await other functions or I/O)
# so they should be as lightweight as possible
orderbooks = SortedDict()
# conn = tools.db.get_connection()


async def book(feed, pair, book, timestamp):
    """
    Run code every time websocket sends an update
    :param feed: which exchange the feed comes from
    :param pair: currency pair of update
    :param book: copy of updated order book
    :param timestamp: timestamp of update
    :return
    """
    global orderbooks

    # if new update changes best bid/ask
    try:
        if orderbooks[pair] != {"bid": book[BID].items()[-1], "ask": book[ASK].items()[0]}:
            update_database(book, pair)
        else:
            pass

    # if database table doesn't already exist, create it
    except KeyError as e:
        update_database(book, pair)

    # print("--- {:.15f} ---".format(time.clock() - start_time))


def update_database(book, pair):
    global orderbooks
    orderbooks[pair] = {
        "bid": book[BID].items()[-1],
        "ask": book[ASK].items()[0],
    }
    streamable_updates = (run_orderbook(orderbooks, pair))
    for combination, profit in streamable_updates.items(): pass
        # r.db('arbitrage').table(combination).insert({
        #     "timestamp": r.now(),
        #     "combination": combination,
        #     "profit": profit
        # }).run(conn)

def main():
    """
    Subscribe to all feeds
    """
    logger = logging.getLogger('arbitrage')
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler('arbitrage.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # tools.db.create_database("arbitrage")
    f = FeedHandler()

    f.add_feed(
        Poloniex(
            # channels=poloniex_pair_mapping,
            channels=['BTC-USDT', 'ETH-BTC', 'ETH-USDT'],
            callbacks={L2_BOOK: BookCallback(book)},
        )
    )
    f.run()


if __name__ == "__main__":
    main()
