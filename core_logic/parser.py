# core_logic/parser.py
import spacy

class StatementParser:
    def __init__(self):
        # Load the small English model. It's a good balance of speed and capability.
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading spaCy model 'en_core_web_sm'...")
            from spacy.cli import download
            download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

    def parse(self, sentence: str) -> dict:
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
                subject = token.root.head.text.lower() # A simple start
                # A better way for subject:
                subject_chunk = next(chunk for chunk in doc.noun_chunks if chunk.root == token)
                subject = subject_chunk.text.lower()
                break

        # Find the object (direct object or attribute complement)
        # For "The cat is black", 'black' is an 'acomp' (adjectival complement)
        for token in doc:
            if token.dep_ in ["dobj", "attr", "acomp"]:
                object_chunk = next(chunk for chunk in doc.noun_chunks if chunk.root == token)
                object = object_chunk.text.lower()
                break
        
        if subject and object:
            return {"subject": subject, "object": object, "negated": negated}
        
        return None