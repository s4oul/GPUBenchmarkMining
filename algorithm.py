class Algorithm:
    KAWPOW = 'kawpow'
    AUTOLYKOS2 = 'autolykos2'

    @staticmethod
    def is_valid(algo_name: str) -> bool:
        if algo_name != Algorithm.KAWPOW\
                and algo_name != Algorithm.AUTOLYKOS2:
            return False
        return True
