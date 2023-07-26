class Algorithm:
    KAWPOW = 'kawpow'
    FIROPOW = 'firopow'
    AUTOLYKOS2 = 'autolykos2'
    ETHPOW = 'ethpow'

    @staticmethod
    def is_valid(algo_name: str) -> bool:
        if algo_name != Algorithm.KAWPOW \
                and algo_name != Algorithm.FIROPOW \
                and algo_name != Algorithm.AUTOLYKOS2 \
                and algo_name != Algorithm.ETHPOW:
            return False
        return True
