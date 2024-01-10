class Rn:
    def __init__(self, qs, qe=0):
        '''
        :param qs: skin bearing of pile
        :param qe: end bearing of pile
        '''
        self.Rn = qs + qe
