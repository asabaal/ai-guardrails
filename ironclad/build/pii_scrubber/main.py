from scrub_pii import scrub_pii

__all__ = ['scrub_pii']

def main():
    sample_text = '''Hello John,

    Please contact me at john.doe@example.com or at 192.168.1.1. 
    Call me at (555) 123-4567. 
    Thank you!'''
    try:
        sanitized = scrub_pii(sample_text)
    except Exception as e:
        print(f"Error during scrubbing: {e}")
        return
    print("""Original Text:
""", sample_text)
    print("""Sanitized Text:
""", sanitized)

if __name__ == "__main__":
    main()