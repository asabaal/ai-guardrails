# core_logic/parser.py
import spacy

class StatementParser:
    def __init__(self):
        # Load the small English model. It's a good balance of speed and capability.
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading spaCy model 'en_core_web_sm'...")
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")

    def parse(self, sentence: str) -> dict | None:
        """
        Parses a sentence to extract subject, object, and negation.
        Returns a dictionary or None if parsing fails.
        """
        doc = self.nlp(sentence)
        
        subject = None
        object = None
        negated = False

        # Find negation
        for token in doc:
            if token.dep_ == "neg":
                negated = True
                break
        
        # Find the subject (nominal subject of the root verb)
        for token in doc:
            if token.dep_ == "nsubj":
                # Get the whole noun chunk, not just the token
                for chunk in doc.noun_chunks:
                    if token in chunk:
                        subject = chunk.text.lower()
                        break
                break

        # Find the object (direct object or attribute complement)
        # For "The cat is black", 'black' is an 'acomp' (adjectival complement)
        for token in doc:
            if token.dep_ in ["dobj", "attr", "acomp"]:
                # For adjectives like 'black', use the token text directly
                if token.dep_ in ["attr", "acomp"]:
                    object = token.text.lower()
                else:
                    # For direct objects, try to find the noun chunk
                    for chunk in doc.noun_chunks:
                        if token in chunk:
                            object = chunk.text.lower()
                            break
                break
        
        if subject and object:
            return {"subject": subject, "object": object, "negated": negated}
        
        return None