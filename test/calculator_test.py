from calculator import Calculator
import unittest

class CalculatorTest(unittest.TestCase):
    def setUp(self):
        self.calculator = Calculator()

    def test_balance(self):
        position_keys = ('composition', 'currentPrice', 'currentMarketValue', 'openQuantity')
        position_values = ((.1, 1, 80, 100), (.2, 2, 120, 100), (.7, .5, 600, 100))
        positions = self._generate_list_of_dict(position_keys, position_values)
        balances = { 'totalEquity': 1000, 'marketValue': 800, 'cash': 200 }
        # expected purchases keys
        expected_p_k = ('composition',     'currentPrice',     'currentMarketValue', 'openQuantity',
                        'purchaseValue',   'purchaseQuantity', 'newMarketValue', 'newQuantity',
                        'before actual %', 'after actual %',   'ideal %')
        # expected purchases values
        expected_p_v = ((.1,  1,  80, 100,  20,  20, 100, 120,  8, 10, 10),
                        (.2,  2, 120, 100,  80,  40, 200, 140, 12, 20, 20),
                        (.7, .5, 600, 100, 100, 200, 700, 300, 60, 70, 70))
        # expected purchases
        expected_p = self._generate_list_of_dict(expected_p_k, expected_p_v)

        expected_balances = balances.copy()
        expected_balances.update({ 'newCash': 0, 'newMarketValue': 1000 })

        purchases, new_balances = self.calculator.balance(positions, balances)

        self.assertEqual(expected_p, purchases)
        self.assertEqual(expected_balances, new_balances)

    def test_new_balances(self):
        balances = { 'cash': 5, 'marketValue': 5, 'totalEquity': 10 }
        purchases = [{ 'purchaseValue': 1 } for _ in xrange(4)]
        # python3.6 { **balances, **{ 'newCash': 1, 'newMarketValue': 9 } }
        expected = { 'cash':    5, 'marketValue':    5, 'totalEquity': 10,
                     'newCash': 1, 'newMarketValue': 9 }
        result = self.calculator._new_balances(balances, purchases)
        self.assertEqual(expected, result)

    def test_percentages(self):
        total_equity = 20
        position_values = ((.3, 6, 10, 30, 50, 30),
                           (.3, 2,  0, 10,  0, 30),
                           (.4, 2, 10, 10, 50, 40))
        positions = []
        expected = []
        for a, b, c, d, e, f in position_values:
            x = { 'composition': a, 'currentMarketValue': b, 'newMarketValue': c }
            # python3.6 { **x, **{} }
            y = x.copy()
            y.update({ 'before actual %': d, 'after actual %': e, 'ideal %': f })
            positions.append(x)
            expected.append(y)
        result = self.calculator._percentages(positions, total_equity)
        self.assertEqual(expected, result)

    def test_purchases_all_needed(self):
        positions = [{'composition': .3, 'currentPrice': 2, 'currentMarketValue': 150, 'openQuantity': 100},
                     {'composition': .3, 'currentPrice': 1, 'currentMarketValue': 250, 'openQuantity': 100},
                     {'composition': .4, 'currentPrice': 3, 'currentMarketValue': 250, 'openQuantity': 100}]
        balances = { 'cash': 350, 'marketValue': 650, 'totalEquity': 1000 }
        expected_keys = ('composition', 'currentPrice', 'currentMarketValue', 'openQuantity',
                         'purchaseValue', 'purchaseQuantity', 'newMarketValue', 'newQuantity')
        expected_values = ((.3, 2, 150, 100, 140, 70, 290, 170),
                           (.3, 1, 250, 100,  50, 50, 300, 150),
                           (.4, 3, 250, 100, 150, 50, 400, 150))
        expected = self._generate_list_of_dict(expected_keys, expected_values)
        result = self.calculator._purchases(positions, balances)
        self.assertEqual(expected, result)

    def test_purchases_not_all_needed(self):
        positions = [{'composition': .3, 'currentPrice': 2, 'currentMarketValue': 500, 'openQuantity': 100},
                     {'composition': .3, 'currentPrice': 1, 'currentMarketValue': 150, 'openQuantity': 100},
                     {'composition': .4, 'currentPrice': 5, 'currentMarketValue': 0, 'openQuantity': 100}]
        balances = { 'cash': 350, 'marketValue': 650, 'totalEquity': 1000 }

        # python3.6 => { **positions[0], **{'purchaseValue': 0} }
        expected_keys = ('composition', 'currentPrice', 'currentMarketValue', 'openQuantity',
                         'purchaseValue', 'purchaseQuantity', 'newMarketValue', 'newQuantity')
        expected_values = [(.3, 2, 500, 100,   0,  0, 500, 100),
                           (.3, 1, 150, 100,  60, 60, 210, 160),
                           (.4, 5,   0, 100, 250, 50, 250, 150)]
        expected = self._generate_list_of_dict(expected_keys, expected_values)
        result = self.calculator._purchases(positions, balances)
        self.assertEqual(expected, result)

    def _generate_list_of_dict(self, keys, values):
        return [{ key: entry[i] for i, key in enumerate(keys) } for entry in values]

if __name__ == '__main__':
    unittest.main()

# python -m test.calculator_test