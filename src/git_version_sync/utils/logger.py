from colorful_log import PrintLog, Colors

error = PrintLog().prefix("Error: ").color(Colors.RED)
warning = PrintLog().prefix("Error: ").color(Colors.YELLOW)
info = PrintLog().prefix("Error: ").color(Colors.BLUE)