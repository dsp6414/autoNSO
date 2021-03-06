import numpy as np
import cvxpy as cp

from IPython import embed
from algs.optAlg import OptAlg

class ProxBundle(OptAlg):
    def __init__(self, objective, mu=1.0, null_k=0.5, **kwargs):
        super(ProxBundle, self).__init__(objective, **kwargs)

        self.constraints = []
        self.p = cp.Variable(self.x_dim)  # variable of optimization
        self.v = cp.Variable()  # value of cutting plane model
        self.mu = mu
        self.null_k = null_k
        self.name = 'ProxBundle'
        self.name += ' (mu=' + str(self.mu) + ',null_k=' + str(self.null_k) + ')'

        # Add one bundle point to initial point
        self.cur_x = self.x0
        self.cur_y = self.x0  # the auxiliary variables will null values
        self.path_y = None
        self.total_serious      = 0
        self.total_null         = 0

        # Some other useful info
        self.cur_tight = 0
        self.tight_x = []
        self.tight_y = []

        self.update_params(None)

    def step(self):

        super(ProxBundle, self).step()

        prox_objective = self.v + 0.5 * (self.mu / 2.0) * cp.power(cp.norm(self.p - self.cur_x, 2), 2)
        self.p.value = self.cur_y  # Warm-starting
        prob = cp.Problem(cp.Minimize(prox_objective), self.constraints)

        # Use MOSEK for accuracy
        #        m_params = {'MSK_DPAR_INTPNT_CO_TOL_PFEAS':1e-12}
        #        prob.solve(solver=cp.MOSEK,mosek_params=m_params)

        # If you don't have mosek just do:
        prob.solve(warm_start=True)

        # Update current iterate value and update the bundle
        self.cur_y = self.p.value

        # Find number of tight constraints
        self.cur_duals = [self.constraints[i].dual_value for i in range(len(self.constraints))]
        thres = 1e-6 * max(self.cur_duals)
        self.cur_active = [(self.cur_duals[i] > thres) for i in range(len(self.constraints))]
        self.cur_tight = sum(self.cur_active)

        # Update paths and bundle constraints
        self.update_params(self.v.value)

    def update_params(self, expected):

        super(ProxBundle,self).update_params()

        if self.path_y is not None:
            self.path_y = np.concatenate((self.path_y, self.cur_y[np.newaxis]))
        else:
            self.path_y = self.cur_y[np.newaxis]

        self.tight_y += [self.cur_tight]

        orcl_call = self.objective.call_oracle(self.cur_y)
        cur_fy = orcl_call['f']

        # Whether to take a serious step
        if expected is not None:
            serious = ((self.path_fx[-1] - cur_fy) > self.null_k * (self.path_fx[-1] - expected))
        else:
            serious = True

        if serious:
            self.cur_x = self.cur_y
            self.cur_fx = orcl_call['f']
            if self.path_x is not None:
                self.path_x = np.concatenate((self.path_x, self.cur_x[np.newaxis]))
                self.path_fx = np.concatenate((self.path_fx, self.cur_fx[np.newaxis]))
            else:
                self.path_x = self.cur_x[np.newaxis]
                self.path_fx = self.cur_fx[np.newaxis]

            self.tight_x += [self.cur_tight]

            self.total_serious += 1
        else:
            self.total_null += 1

        self.cur_iter += 1 # Count null steps as interations

        # Even if it is null step, add a constraint to cutting plane model
        self.constraints += [(cur_fy.copy() +
                              orcl_call['df'].copy() @ (self.p - self.cur_y.copy())) <= self.v]

    def save_bundle(self):
        print('Bundled Saving Triggered', flush=True)
        self.saved_bundle = {'bundle': self.path_y[np.array(self.cur_active)],
                             'iter': self.cur_iter}