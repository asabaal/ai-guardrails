import re

class SimpleLogicEngine:
    def __init__(self):
        # Our "memory" of accepted truths
        self.knowledge_base = []
        print("Logic Engine initialized. Ready for statements.")

    def _parse_statement(self, text: str):
        """
        Parses a very simple sentence into a structured format.
        Example: "The cat is not black" -> {'subject': 'the cat', 'object': 'black', 'negated': True}
        """
        # Use a simple regex to find the subject, object, and if it's negated
        # This is a fragile parser, but it's a start.
        pattern = r"(.+?)\s+(is not|is)\s+(.+)"
        match = re.match(pattern, text, re.IGNORECASE)

        if not match:
            return None # Couldn't parse the sentence

        subject = match.group(1).strip().lower()
        verb_phrase = match.group(2).strip().lower()
        object = match.group(3).strip().lower()

        is_negated = (verb_phrase == "is not")

        return {
            "subject": subject,
            "object": object,
            "negated": is_negated
        }

    def process_statement(self, text: str):
        """
        The main function: takes a statement, checks for contradictions,
        and adds it to the knowledge base if it's new.
        """
        parsed = self._parse_statement(text)
        if not parsed:
            print(f"  -> Could not understand: '{text}'")
            return

        # Check for contradiction against existing knowledge
        contradiction_found = False
        for known_fact in self.knowledge_base:
            if (known_fact['subject'] == parsed['subject'] and
                known_fact['object'] == parsed['object'] and
                known_fact['negated'] != parsed['negated']):
                
                print(f"  -> CONTRADICTION DETECTED!")
                print(f"     You stated: '{text}'")
                # Reconstruct the original statement for clarity
                original_fact = f"{known_fact['subject'].capitalize()} is {'not ' if known_fact['negated'] else ''}{known_fact['object']}"
                print(f"     But you previously stated: '{original_fact}'")
                contradiction_found = True
                break # Stop after finding the first contradiction

        if not contradiction_found:
            # Check if it's just a repeat of existing knowledge
            is_duplicate = any(
                known_fact['subject'] == parsed['subject'] and
                known_fact['object'] == parsed['object'] and
                known_fact['negated'] == parsed['negated']
                for known_fact in self.knowledge_base
            )

            if is_duplicate:
                print(f"  -> OK (Already known): '{text}'")
            else:
                print(f"  -> OK (New fact): '{text}'")
                self.knowledge_base.append(parsed)

# --- How to run it ---
if __name__ == "__main__":
    engine = SimpleLogicEngine()

    conversation = [
        "The sky is blue",
        "The cat is black",
        "The cat is not black",  # Contradiction!
        "The sky is not green",  # Different object, no contradiction
        "The sky is blue",       # Duplicate
        "My car is red",
        "My car is not red"      # Contradiction!
    ]

    for line in conversation:
        print(f"\nProcessing: '{line}'")
        engine.process_statement(line)

    print("\n--- Final Knowledge Base ---")
    print(engine.knowledge_base)