import numpy as np

def get_cplimits_sym(num, den, num_err, den_err):

        # Clopper-Pearson errors
        # tail = (1 - cl) / 2
        # 2sigma (95% CL): tail = (1 - 0.95) / 2 = 0.025
        # 1sigma (68% CL): tail = (1 - 0.68) / 2 = 0.16
        tail = 0.16
        n_num = pow(num/num_err, 2.)
        n_den = pow(den/den_err, 2.)

        # nom
        n_rat = n_num / n_den

        # lower limit
        q_low = ROOT.Math.fdistribution_quantile_c(1 - tail, n_num * 2,
                (n_den + 1) * 2)
        r_low = q_low * n_num / (n_den + 1)

        # upper limit
        q_high = ROOT.Math.fdistribution_quantile_c(tail, (n_num + 1) * 2,
                n_den * 2)
        r_high = q_high * (n_num + 1) / n_den

        # lower, upper errors
        err_lo, err_hi = n_rat - r_low, r_high - n_rat

        #return err_lo, err_hi
        #err_ = np.sqrt(np.mean(np.array([err_lo, err_hi])**2))
        err_ = err_lo if num/den > 1. else err_hi
        return err_
