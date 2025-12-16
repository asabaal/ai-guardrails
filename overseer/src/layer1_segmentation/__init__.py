"""
Layer 1: Segmentation Components
Components responsible for breaking text into logical steps.

Following AI Safety Development Protocols (AI_SAFETY_DEVELOPMENT_PROTOCOLS.md)
"""

try:
    from .text_segmenter import TextSegmenter, RuleBasedSplitter, Normalizer, Aggregator
except ImportError:
    # Fallback for development environment
    TextSegmenter = None
    RuleBasedSplitter = None
    Normalizer = None
    Aggregator = None

__all__ = ['TextSegmenter', 'RuleBasedSplitter', 'Normalizer', 'Aggregator']