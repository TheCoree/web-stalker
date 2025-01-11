from datetime import datetime

class Messages:
    """Handles styled console messages."""

    @staticmethod
    def log(message_type, color_code, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[\033[1;{color_code}m{message_type}\033[0m] {timestamp} - {message}")

    @staticmethod
    def info(message):
        Messages.log("INFO", "32", message)

    @staticmethod
    def warn(message):
        Messages.log("WARN", "93", message)

    @staticmethod
    def error(message):
        Messages.log("ERROR", "31", message)

    @staticmethod
    def success(message):
        Messages.log("SUCCESS", "96", message)

    @staticmethod
    def banner():
        art = r"""                __               __        ____            
 _      _____  / /_        _____/ /_____ _/ / /_____  _____
| | /| / / _ \/ __ \______/ ___/ __/ __ `/ / //_/ _ \/ ___/
| |/ |/ /  __/ /_/ /_____(__  ) /_/ /_/ / / ,< /  __/ /    
|__/|__/\___/_.___/     /____/\__/\__,_/_/_/|_|\___/_/  made by corede

        """
        print(f"\033[1;34m{art}\033[0m")