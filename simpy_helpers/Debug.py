class Debug:
    """
    Use this class to add debug statements to simulation output
    Doesn't necessarily need to be used outside of this file... but could be
    """
    DEBUG = False
    @staticmethod
    def info(msg):
        if Debug.DEBUG:
            print(msg)