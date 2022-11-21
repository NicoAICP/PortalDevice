class Logger:
    """Logger
    """
    
    DEBUG = "DEBUG"
    INFO  = "INFO"
    ERROR = "ERROR"

    def __init__(self, logger_name: str, logger_file: str) -> None:
        """Create logger
        """
        self.logger_name = logger_name
        self.logger_file = logger_file

    def log(self, level: str, msg: str) -> None:
        with open(self.logger_file, "a") as fp:
            fp.write(self.logger_name + ":\t\t" + level + "\t->\t" + msg + "\n")
            fp.flush()
            fp.close()


