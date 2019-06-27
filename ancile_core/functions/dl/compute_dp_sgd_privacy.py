# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math


from ancile_core.functions.dl.rdp_accountant import compute_rdp
from ancile_core.functions.dl.rdp_accountant import get_privacy_spent



def apply_dp_sgd_analysis(N, batch_size, noise_multiplier, epochs, delta=1e-6):
  q = batch_size / N  # q - the sampling ratio.


  orders = ([1.25, 1.5, 1.75, 2., 2.25, 2.5, 3., 3.5, 4., 4.5] +
            list(range(5, 64)) + [128, 256, 512])

  steps = int(math.ceil(epochs * N / batch_size))


  """Compute and print results of DP-SGD analysis."""
  sigma = noise_multiplier
  rdp = compute_rdp(q, sigma, steps, orders)

  eps, _, opt_order = get_privacy_spent(orders, rdp, target_delta=delta)

  print('DP-SGD with sampling rate = {:.3g}% and noise_multiplier = {} iterated'
        ' over {} steps satisfies'.format(100 * q, sigma, steps), end=' ')
  print('differential privacy with eps = {:.3g} and delta = {}.'.format(
      eps, delta))
  print('The optimal RDP order is {}.'.format(opt_order))

  if opt_order == max(orders) or opt_order == min(orders):
    print('The privacy estimate is likely to be improved by expanding '
          'the set of orders.')

  return eps
