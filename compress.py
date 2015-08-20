import sys, pickle
from pulp import *
import numpy as np

def compress(sentence, start_prob, lm):
    num_variables = 0
    def d():
        nonlocal num_variables
        lpv = LpVariable('v' + str(num_variables), 0, 1, LpBinary)
        num_variables += 1
        return lpv

    num_mrphs = len(sentence)

    sentence.insert(0, '<START>')

    problem = LpProblem('compression', LpMaximize)

    # set variables of delta
    delta = []
    for i in range(num_mrphs + 1):
        delta.append(d())

    dummy = LpVariable('dummy', 0, 0)

    delta[0] = dummy
    
    # initialize all variables (alpha, beta, gumma) to dummy variables
    alpha = np.ndarray((num_mrphs + 1, ), LpVariable)
    alpha_coeff = np.ndarray((num_mrphs + 1, ), float)
    
    for i in range(num_mrphs + 1):
        alpha[i] = dummy
        alpha_coeff[i] = 0

    beta = np.ndarray((num_mrphs + 1, num_mrphs + 1), LpVariable)
    beta_coeff = np.ndarray((num_mrphs + 1, num_mrphs + 1), float)

    for i in range(num_mrphs + 1):
        for j in range(num_mrphs + 1):
            beta[i][j] = dummy
            beta_coeff[i][j] = 0

    gumma = np.ndarray((num_mrphs + 1, num_mrphs + 1, num_mrphs + 1), LpVariable)
    gumma_coeff = np.ndarray((num_mrphs + 1, num_mrphs + 1, num_mrphs + 1), float)
    for i in range(num_mrphs + 1):
        for j in range(num_mrphs + 1):
            for k in range(num_mrphs + 1):
                gumma[i][j][k] = dummy
                gumma_coeff[i][j][k] = 0

    # assign unique variables to alphas, betas, gummas and assign actual coefficients
    for i in range(1, num_mrphs + 1):
        alpha[i] = d()
        alpha_coeff[i] = start_prob[sentence[i]]

    for i in range(num_mrphs):
        for j in range(i+1, num_mrphs + 1):
            beta[i][j] = d()
            try:
                beta_coeff[i][j] = lm[(sentence[i], sentence[j])]['<END>\n']
            except KeyError:
                beta_coeff[i][j] = 0
    for i in range(num_mrphs + 1 - 2):
        for j in range(i+1, num_mrphs + 1 - 1):
            for k in range(j+1, num_mrphs + 1):
                gumma[i][j][k] = d()
                try:
                    gumma_coeff[i][j][k] = lm[(sentence[i], sentence[j])][sentence[k]]
                except KeyError:
                    gumma_coeff[i][j] = 0


    # write Constraints

    # Constraint 1
    problem += lpDot(np.ones(num_mrphs, int), alpha[1:]) == 1

    # Constraint 2
    for k in range(1, num_mrphs + 1):
        constraint2k = LpAffineExpression()
        constraint2k += delta[k] - alpha[k]
        for i in range(k - 1):
            for j in range(1, k):
                constraint2k -= gumma[i][j][k]
        problem += constraint2k == 0

    # Constraint 3
    for j in range(1, num_mrphs + 1):
        constraint3j = LpAffineExpression()
        constraint3j += delta[j]
        for i in range(0, j):
            for k in range(j+1, num_mrphs + 1):
                constraint3j -= gumma[i][j][k]
        for i in range(j):
            constraint3j -= beta[i][j]
        problem += constraint3j == 0
    
    # Constraint 4
    for i in range(1, num_mrphs + 1):
        constraint4i = LpAffineExpression()
        constraint4i += delta[i]
        for j in range(i+1, num_mrphs):
            for k in range(j+1, num_mrphs + 1):
                constraint4i -= gumma[i][j][k]
        for j in range(i+1, num_mrphs + 1):
            constraint4i -= beta[i][j]
        for h in range(i):
            constraint4i -= beta[h][i]
        problem += constraint4i == 0

    # Constraint 5
    constraint5 = LpAffineExpression()
    for i in range(num_mrphs):
        for j in range(i+1, num_mrphs + 1):
            constraint5 += beta[i][j]
    problem += constraint5 == 1


    # Minimum Length Constraint
    problem += lpSum(delta[1:]) >= len(sentence) / 3
    
    # Now, solve the ILP problem
    status = problem.solve()

    compressed_sentence = []
    for i in range(1, num_mrphs + 1):
        if value(delta[i]) == 1:
            compressed_sentence.append(sentence[i])

    return compressed_sentence
