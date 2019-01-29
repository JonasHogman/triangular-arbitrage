import unittest
import arbitrage
import tools.arbitragecalculation
import tools.db
from decimal import Decimal


class TestArbitrage(unittest.TestCase):
    def test_test_calculation(self):
        test_dict = {"BTC_ETH": {"asks": ['0.03195317', '0.00690458'], "bids": ['0.03194500', '88.0035']},
                     "ETH_ZEC": {"asks": ['0.45188710', '10.359'], "bids": ['0.44852871', '34.7527209']},
                     "BTC_ZEC": {"asks": ['0.01440500', '48.8819'], "bids": ['0.01440000', '0.25514799']}}

        self.assertEqual(tools.arbitragecalculation.test_calculation(test_dict["BTC_ETH"], test_dict["ETH_ZEC"],
                                                                     test_dict["BTC_ZEC"], 0, 100, 100, 100),
                         Decimal('0.99728342'))

    def test_calculate_lowest_amount(self):
        test_dict = {"BTC_ETH": {"asks": [0.03195317, 0.00690458], "bids": [0.03194500, 88.0035]},
                     "ETH_ZEC": {"asks": [0.45188710, 10.359], "bids": [0.44852871, 34.7527209]},
                     "BTC_ZEC": {"asks": [0.01440500, 48.8819], "bids": [0.01440000, 0.25514799]}}

        self.assertEqual(
            tools.arbitragecalculation.calculate_lowest_amount(test_dict["BTC_ETH"], test_dict["ETH_ZEC"],
                                                               test_dict["BTC_ZEC"], 1, 0),
            Decimal('0.86801050'))

        self.assertEqual(
            tools.arbitragecalculation.calculate_lowest_amount(test_dict["BTC_ETH"], test_dict["ETH_ZEC"],
                                                               test_dict["BTC_ZEC"], 2, 0),
            Decimal('0.86990000'))

    # def test_calculate_triangle_both_ways(self):
    #     test_dict = [{
    #         'bid': (Decimal('1.38705'), Decimal('10')),
    #         'ask': (Decimal('1.38710'), Decimal('10'))
    #     }, {
    #         'bid': (1 / Decimal('1.59440'), Decimal('10')),
    #         'ask': (1 / Decimal('1.59455'), Decimal('10'))
    #     }, {
    #         'bid': (Decimal('0.86975'), Decimal('10')),
    #         'ask': (Decimal('0.86990'), Decimal('10'))
    #     }]
    #
    #     self.assertEqual(
    #         tools.arbitragecalculation.calculate_triangle_both_ways(test_dict[0], test_dict[1], test_dict[2], "EUR",
    #                                                                 "USD", "GBP", 0),
    #         0.005872)


if __name__ == "__main__":
    unittest.main()
