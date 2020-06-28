import math

'''
Function to calcualte the positive rate
Arguments
    new_case: number of new cases
    new_test: number of new tests
'''
def calculate_positive_rate(new_case, new_test):

    if new_case and new_test:
        rate = (new_case/new_test ) * 100
        if math.isnan(rate):
            return ''

        return rate
    
    return ''

