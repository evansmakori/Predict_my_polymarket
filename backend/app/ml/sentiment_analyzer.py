"""
AI-Powered Sentiment Analysis for Market Descriptions.

Uses NLP models to analyze market descriptions and extract sentiment,
key topics, and confidence indicators.
"""

import logging
from typing import Dict, List, Optional
import re
from collections import Counter

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available. Using fallback sentiment analysis.")

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    AI-powered sentiment analysis for market descriptions.
    
    Analyzes:
    - Overall sentiment (positive/negative/neutral)
    - Confidence level in the outcome
    - Key topics and entities
    - Uncertainty indicators
    - Market bias detection
    """
    
    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        self.model_name = model_name
        self.sentiment_pipeline = None
        self.device = "cuda" if TRANSFORMERS_AVAILABLE and torch.cuda.is_available() else "cpu"
        
        if TRANSFORMERS_AVAILABLE:
            try:
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model=self.model_name,
                    device=0 if self.device == "cuda" else -1
                )
                logger.info(f"Sentiment analyzer initialized on {self.device}")
            except Exception as e:
                logger.error(f"Error loading sentiment model: {e}")
                self.sentiment_pipeline = None
        
        # Keywords for uncertainty detection
        self.uncertainty_keywords = {
            'high': ['might', 'maybe', 'possibly', 'uncertain', 'unclear', 'could', 'may'],
            'medium': ['likely', 'probably', 'expected', 'anticipated', 'should'],
            'low': ['will', 'definitely', 'certainly', 'confirmed', 'guaranteed']
        }
        
        # Topic keywords
        self.topic_categories = {
            'politics': ['election', 'vote', 'president', 'senate', 'congress', 'political', 'campaign'],
            'sports': ['game', 'match', 'team', 'player', 'championship', 'win', 'score'],
            'crypto': ['bitcoin', 'ethereum', 'crypto', 'blockchain', 'token', 'defi', 'nft'],
            'economics': ['gdp', 'inflation', 'economy', 'market', 'stock', 'recession', 'growth'],
            'technology': ['ai', 'tech', 'software', 'launch', 'release', 'innovation'],
            'entertainment': ['movie', 'show', 'award', 'box office', 'streaming', 'series']
        }
    
    def analyze(self, text: str, market_data: Optional[Dict] = None) -> Dict:
        """
        Perform comprehensive sentiment analysis on market text.
        
        Args:
            text: Market description or question
            market_data: Additional market context
        
        Returns:
            Dictionary with sentiment analysis results
        """
        if not text:
            return self._empty_result()
        
        # Use transformer model if available
        if TRANSFORMERS_AVAILABLE and self.sentiment_pipeline:
            ml_sentiment = self._ml_sentiment_analysis(text)
        else:
            ml_sentiment = None
        
        # Rule-based analysis (always run as backup)
        rule_based = self._rule_based_analysis(text)
        
        # Combine results
        result = {
            'sentiment': ml_sentiment['label'] if ml_sentiment else rule_based['sentiment'],
            'sentiment_score': ml_sentiment['score'] if ml_sentiment else rule_based['sentiment_score'],
            'confidence': self._calculate_confidence(text, market_data),
            'uncertainty_level': rule_based['uncertainty_level'],
            'key_topics': rule_based['topics'],
            'word_count': len(text.split()),
            'has_question': '?' in text,
            'has_dates': bool(re.search(r'\d{4}|\d{1,2}/\d{1,2}', text)),
            'bias_indicators': self._detect_bias(text),
            'complexity_score': self._calculate_complexity(text),
            'model_type': 'transformer' if ml_sentiment else 'rule_based'
        }
        
        return result
    
    def _ml_sentiment_analysis(self, text: str) -> Optional[Dict]:
        """Use transformer model for sentiment analysis."""
        try:
            # Split long texts into chunks
            max_length = 512
            words = text.split()
            
            if len(words) > max_length:
                # Analyze first and last parts
                first_part = ' '.join(words[:max_length//2])
                last_part = ' '.join(words[-max_length//2:])
                
                result1 = self.sentiment_pipeline(first_part)[0]
                result2 = self.sentiment_pipeline(last_part)[0]
                
                # Average scores
                avg_score = (result1['score'] + result2['score']) / 2
                label = result1['label'] if result1['score'] > result2['score'] else result2['label']
                
                return {'label': label, 'score': avg_score}
            else:
                result = self.sentiment_pipeline(text)[0]
                return result
        
        except Exception as e:
            logger.error(f"ML sentiment analysis error: {e}")
            return None
    
    def _rule_based_analysis(self, text: str) -> Dict:
        """Rule-based sentiment analysis as fallback."""
        text_lower = text.lower()
        
        # Positive and negative word lists
        positive_words = ['win', 'yes', 'pass', 'succeed', 'approve', 'victory', 'gain', 'rise', 'increase']
        negative_words = ['lose', 'no', 'fail', 'reject', 'defeat', 'loss', 'fall', 'decrease', 'decline']
        
        # Count occurrences
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        # Calculate sentiment
        total = pos_count + neg_count
        if total == 0:
            sentiment = 'NEUTRAL'
            score = 0.5
        elif pos_count > neg_count:
            sentiment = 'POSITIVE'
            score = 0.5 + (pos_count / (total * 2))
        else:
            sentiment = 'NEGATIVE'
            score = 0.5 - (neg_count / (total * 2))
        
        # Detect uncertainty
        uncertainty = self._detect_uncertainty(text_lower)
        
        # Detect topics
        topics = self._detect_topics(text_lower)
        
        return {
            'sentiment': sentiment,
            'sentiment_score': score,
            'uncertainty_level': uncertainty,
            'topics': topics
        }
    
    def _detect_uncertainty(self, text: str) -> str:
        """Detect level of uncertainty in text."""
        uncertainty_counts = {
            'high': sum(1 for word in self.uncertainty_keywords['high'] if word in text),
            'medium': sum(1 for word in self.uncertainty_keywords['medium'] if word in text),
            'low': sum(1 for word in self.uncertainty_keywords['low'] if word in text)
        }
        
        max_level = max(uncertainty_counts, key=uncertainty_counts.get)
        
        if uncertainty_counts[max_level] == 0:
            return 'medium'
        
        return max_level
    
    def _detect_topics(self, text: str) -> List[str]:
        """Detect main topics in the text."""
        detected_topics = []
        
        for category, keywords in self.topic_categories.items():
            if any(keyword in text for keyword in keywords):
                detected_topics.append(category)
        
        return detected_topics if detected_topics else ['general']
    
    def _calculate_confidence(self, text: str, market_data: Optional[Dict]) -> float:
        """Calculate confidence in the sentiment analysis."""
        confidence = 0.6  # Base confidence
        
        # Adjust based on text length
        word_count = len(text.split())
        if word_count > 20:
            confidence += 0.1
        if word_count > 50:
            confidence += 0.1
        
        # Adjust based on market data
        if market_data:
            if market_data.get('volume_24h', 0) > 10000:
                confidence += 0.1
            if market_data.get('num_trades', 0) > 100:
                confidence += 0.1
        
        return min(confidence, 0.95)
    
    def _detect_bias(self, text: str) -> Dict:
        """Detect potential biases in the text."""
        text_lower = text.lower()
        
        bias_indicators = {
            'loaded_language': False,
            'one_sided': False,
            'emotional_language': False
        }
        
        # Loaded language
        loaded_words = ['obviously', 'clearly', 'everyone knows', 'undoubtedly']
        bias_indicators['loaded_language'] = any(word in text_lower for word in loaded_words)
        
        # Emotional language
        emotional_words = ['amazing', 'terrible', 'disaster', 'incredible', 'awful']
        bias_indicators['emotional_language'] = any(word in text_lower for word in emotional_words)
        
        return bias_indicators
    
    def _calculate_complexity(self, text: str) -> float:
        """Calculate text complexity score."""
        words = text.split()
        if not words:
            return 0.0
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Sentence count
        sentence_count = max(text.count('.') + text.count('!') + text.count('?'), 1)
        
        # Words per sentence
        words_per_sentence = len(words) / sentence_count
        
        # Complexity score (0-1)
        complexity = min((avg_word_length / 10 + words_per_sentence / 30) / 2, 1.0)
        
        return complexity
    
    def _empty_result(self) -> Dict:
        """Return empty result structure."""
        return {
            'sentiment': 'NEUTRAL',
            'sentiment_score': 0.5,
            'confidence': 0.0,
            'uncertainty_level': 'high',
            'key_topics': [],
            'word_count': 0,
            'has_question': False,
            'has_dates': False,
            'bias_indicators': {},
            'complexity_score': 0.0,
            'model_type': 'none'
        }
    
    def batch_analyze(self, texts: List[str]) -> List[Dict]:
        """Analyze multiple texts in batch."""
        return [self.analyze(text) for text in texts]
    
    def get_model_info(self) -> Dict:
        """Get information about the sentiment model."""
        return {
            'model_loaded': self.sentiment_pipeline is not None,
            'model_name': self.model_name,
            'device': self.device,
            'transformers_available': TRANSFORMERS_AVAILABLE,
            'gpu_available': torch.cuda.is_available() if TRANSFORMERS_AVAILABLE else False
        }
