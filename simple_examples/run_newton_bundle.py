#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 10:18:22 2019

@author: Xiaoyan
"""

# Uses the prox-bundle method to solve the simple objective starting at (2,3)

#%%
import sys
import torch

from vis.visualize import OptPlot
from obj.objective import Objective
from obj.obj_funcs import Simple2D, StronglyConvex
from algs.newton_bundle import NewtonBundle

# Run prox-bundle optimization algorithm
optAlg0 = NewtonBundle(Simple2D, x0=[10,3], max_iter=50, k=2)
optAlg0.optimize()

opt_plot = OptPlot(opt_algs=[optAlg0])
opt_plot.plotPath()
opt_plot.plotValue()