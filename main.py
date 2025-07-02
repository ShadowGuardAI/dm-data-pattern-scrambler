import argparse
import logging
import re
import random
import sys

from faker import Faker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataPatternScrambler:
    """
    Replaces identifiable data patterns with random but valid patterns.
    """

    def __init__(self, locale='en_US'):
        """
        Initializes the DataPatternScrambler with a Faker instance.

        Args:
            locale (str, optional): The locale for generating fake data. Defaults to 'en_US'.
        """
        self.fake = Faker(locale)
        self.patterns = {
            "phone_number": r"(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})",
            "credit_card": r"(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|6(?:011|5[0-9]{2})[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|(?:2131|1800|35\d{3})\d{11})",
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "ip_address": r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)",
        }

    def scramble_text(self, text, pattern_names=None):
        """
        Scrambles identifiable patterns within the given text.

        Args:
            text (str): The text to scramble.
            pattern_names (list, optional): A list of pattern names to scramble. If None, all patterns are used. Defaults to None.

        Returns:
            str: The scrambled text.
        """
        if pattern_names is None:
            pattern_names = self.patterns.keys()

        for pattern_name in pattern_names:
            if pattern_name not in self.patterns:
                logging.warning(f"Unknown pattern name: {pattern_name}. Skipping.")
                continue

            pattern = self.patterns[pattern_name]
            text = self.replace_pattern(text, pattern, pattern_name)

        return text

    def replace_pattern(self, text, pattern, pattern_name):
        """
        Replaces all occurrences of a given pattern with a fake value.

        Args:
            text (str): The text to process.
            pattern (str): The regular expression pattern.
            pattern_name (str): The name of the pattern (used to determine replacement).

        Returns:
            str: The text with the pattern replaced.
        """
        try:
            text = re.sub(pattern, lambda match: self.generate_fake_value(pattern_name, match), text)
            return text
        except re.error as e:
            logging.error(f"Error in regular expression: {e}")
            return text # Return the original text if there's a regex error

    def generate_fake_value(self, pattern_name, match):
        """
        Generates a fake value based on the identified pattern.

        Args:
            pattern_name (str): The name of the pattern.
            match (re.Match): The matched object.

        Returns:
            str: A fake value.
        """
        try:
            if pattern_name == "phone_number":
                return self.fake.phone_number()
            elif pattern_name == "credit_card":
                return self.fake.credit_card_number()
            elif pattern_name == "email":
                return self.fake.email()
            elif pattern_name == "ip_address":
                return self.fake.ipv4()
            else:
                logging.warning(f"No faker method for pattern: {pattern_name}")
                return match.group(0)  # Return original if no faker method exists
        except Exception as e:
            logging.error(f"Error generating fake value for {pattern_name}: {e}")
            return match.group(0)  # Return original on error

def setup_argparse():
    """
    Sets up the command-line argument parser.

    Returns:
        argparse.ArgumentParser: The argument parser.
    """
    parser = argparse.ArgumentParser(description="Scramble identifiable data patterns in text.")
    parser.add_argument("input_text", nargs="?", type=str, help="The input text to scramble. If not provided, reads from stdin.")
    parser.add_argument("-p", "--patterns", nargs="+", type=str, help="List of patterns to scramble (phone_number, credit_card, email, ip_address).  If not provided, all patterns are used.", default=None)
    parser.add_argument("-l", "--locale", type=str, help="Locale for generating fake data (e.g., en_US, fr_FR).", default="en_US")
    parser.add_argument("-f", "--file", type=str, help="Path to a file to scramble. Overrides input_text argument if present.")
    parser.add_argument("-o", "--output", type=str, help="Path to the output file. If not provided, prints to stdout.")


    return parser


def main():
    """
    Main function to parse arguments, scramble data, and output results.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    # Input validation
    valid_patterns = ["phone_number", "credit_card", "email", "ip_address"]
    if args.patterns:
        for pattern in args.patterns:
            if pattern not in valid_patterns:
                logging.error(f"Invalid pattern: {pattern}.  Must be one of: {', '.join(valid_patterns)}")
                sys.exit(1)


    try:
        # Determine the input source
        if args.file:
            try:
                with open(args.file, 'r') as f:
                    input_text = f.read()
            except FileNotFoundError:
                logging.error(f"File not found: {args.file}")
                sys.exit(1)
            except IOError as e:
                logging.error(f"Error reading file: {e}")
                sys.exit(1)
        elif args.input_text:
            input_text = args.input_text
        else:
            # Read from stdin
            input_text = sys.stdin.read()

        scrambler = DataPatternScrambler(args.locale)
        scrambled_text = scrambler.scramble_text(input_text, args.patterns)

        # Determine the output destination
        if args.output:
            try:
                with open(args.output, 'w') as f:
                    f.write(scrambled_text)
                logging.info(f"Scrambled data written to: {args.output}")
            except IOError as e:
                logging.error(f"Error writing to file: {e}")
                sys.exit(1)
        else:
            print(scrambled_text)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)



if __name__ == "__main__":
    main()

# Usage Examples:
# 1. Scramble text from stdin and print to stdout:
#    python main.py < input.txt
#
# 2. Scramble text from a file and print to stdout:
#    python main.py -f input.txt
#
# 3. Scramble text and save to a file:
#    python main.py -f input.txt -o output.txt
#
# 4. Scramble specific patterns (phone number and credit card):
#    python main.py -f input.txt -p phone_number credit_card
#
# 5. Scramble text with a specific locale (French):
#    python main.py -f input.txt -l fr_FR
#
# 6. Scramble inline text and print to stdout:
#    python main.py "My phone number is 555-123-4567 and my credit card is 1234567890123456"