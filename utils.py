# utils.py
# Helper functions for UI display and formatting

class Theme:
    """
    Console color styling
    """

    CYAN = "\033[96m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"


class View:
    """
    Handles user interface display in the console
    """

    @staticmethod
    def draw_header(title, color=Theme.CYAN):
        print(f"\n{color}{'=' * 40}")
        print(f"{title.center(40)}")
        print(f"{'=' * 40}{Theme.RESET}")

    @staticmethod
    def show_menu(options):
        """
        Displays menu options
        """

        for i, option in enumerate(options, 1):
            print(f"{Theme.CYAN}{i}.{Theme.RESET} {option}")

        choice = input("\nSelect option: ")
        return choice

    @staticmethod
    def show_message(message, color=Theme.GREEN):
        """
        Displays formatted messages
        """

        print(f"{color}{message}{Theme.RESET}")

    @staticmethod
    def display_results(candidates):
        """
        Shows voting results in a simple bar chart
        """

        print("\nElection Results:\n")

        for candidate in candidates:
            bar = "█" * candidate.votes
            print(f"{candidate.full_name:15} | {bar} ({candidate.votes})")