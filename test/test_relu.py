import unittest
import numpy as np
import tenseal as ts

import test_helper
from thex import cxt_man
from thex import logger
from thex.ContextManager import ContextManager

class TestReLU(unittest.TestCase):

    def test_ReLU(self):
        # create a random tensor
        tensor = ts.ckks_vector(cxt_man, [1, 2, 3])
        # encrypt tensor
        enc_tensor = tensor.encrypt()

        # apply ReLU function
        result = ReLU(enc_tensor, self.context_manager)

        # check if result is of the correct type
        self.assertIsInstance(result, ts.ckks_vector)

        # check if the result is the same shape as the input tensor
        self.assertEqual(result.shape, tensor.shape)

        # decrypt and check the values
        decrypted_result = result.decrypt()
        expected_result = np.maximum(tensor.decrypt(), np.zeros_like(tensor.decrypt()))
        np.testing.assert_array_almost_equal(decrypted_result, expected_result)


if __name__ == '__main__':
    unittest.main()