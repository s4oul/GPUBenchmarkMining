class Algorithm:
    KAWPOW = 'kawpow'

    @staticmethod
    def is_valid(algo_name: str) -> bool:
        if algo_name != Algorithm.KAWPOW:
            return False
        return True