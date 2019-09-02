#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 10:18:22 2019

@author: Xiaoyan
"""
# Defines an objective
# Calls the oracle
# Oracle will output evaluation and gradient, unless told otherwise

import sys
sys.path.append('..')
from obj.objective import Objective

def lewis_overton2D(x):
    return abs(x[0]) + x[1]**2

Lewis_Overton2D = Objective(lewis_overton2D)
out = Lewis_Overton2D.call_oracle([1,2])

print(out)
# {'f': array(5., dtype=float32), 'df': array([1., 4.], dtype=float32)}
