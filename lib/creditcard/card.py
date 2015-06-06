#coding:utf-8
import unittest


def validate_card_no(cart_no):
    # 校验信用卡号码的正确性
    # http://www.oreilly.com.tw/product_security.php?id=a052_sample

    weight = 2 if len(cart_no) % 2 == 0 else 1
    sum_weigth = 0
    for i in cart_no:
        val = int(i) * weight
        if val > 9:
            val -= 9
        sum_weigth += val

        weight = 1 if weight == 2 else 2

    return sum_weigth % 10 == 0


class autoTestCase(unittest.TestCase):

    def testValidate(self):

        self.assertTrue(validate_card_no("377777777777770"))
        self.assertTrue(validate_card_no("5031161820531715"))
        self.assertTrue(validate_card_no("5031770063501571"))
        self.assertTrue(validate_card_no("5424781841687041"))

        self.assertFalse(validate_card_no("377777777777772"))
        self.assertFalse(validate_card_no("5031161820531716"))
        self.assertFalse(validate_card_no("5031770063501572"))

if __name__ == "__main__":

    unittest.main()


