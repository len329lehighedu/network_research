def extra_infection_cost(k, pi, beta, L_day, gamma):
    # L_new = L_day / gamma
    L_new = L_day / gamma
    # return L_new * (1-pi) * [1-(1-pi*beta)^k]
    return L_new * (1-pi) * (1-(1-pi*beta)**k)


def attendance_gain(k, pi, beta, L_day, gamma, c, v):
    # return: c + k*v - extra_infection_cost(...)
    return c + k*v - extra_infection_cost(k, pi, beta, L_day, gamma)