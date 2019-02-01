import unittest
import tools.arbitragecalculation
from decimal import Decimal
from sortedcontainers import SortedDict


class TestArbitrage(unittest.TestCase):
    # def test_test_calculation(self):
    #     test_dict = {"BTC_ETH": {"ask": ['0.03195317', '0.00690458'], "bid": ['0.03194500', '88.0035']},
    #                  "ETH_ZEC": {"ask": ['0.45188710', '10.359'], "bid": ['0.44852871', '34.7527209']},
    #                  "BTC_ZEC": {"ask": ['0.01440500', '48.8819'], "bid": ['0.01440000', '0.25514799']}}
    #
    #     self.assertEqual(tools.arbitragecalculation.test_calculation(test_dict["BTC_ETH"], test_dict["ETH_ZEC"],
    #                                                                  test_dict["BTC_ZEC"], 0, 100, 100, 100),
    #                      Decimal('-0.00000060'))

    def test_run_orderbook(self):
        test_dict = SortedDict({'BTC-USDT': {'bid': (Decimal('3460.38553834'), Decimal('0.00030398')),
                                             'ask': (Decimal('3460.76469000'), Decimal('0.18249946'))},
                                'ETH-BTC': {'bid': (Decimal('0.03131000'), Decimal('92.72890000')),
                                            'ask': (Decimal('0.03131039'), Decimal('0.81763919'))},
                                'ETH-USDT': {'bid': (Decimal('108.34371001'), Decimal('11.01928628')),
                                             'ask': (Decimal('108.35014997'), Decimal('2.75513919'))}})

        self.assertEqual(tools.arbitragecalculation.run_orderbook(test_dict, 'BTC-USDT'), {'USDT_BTC_ETH': Decimal('-0.00005319')})


if __name__ == "__main__":
    unittest.main()
