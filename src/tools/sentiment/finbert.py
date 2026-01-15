from typing import List, Dict, Union
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

class FinBERT:
    _instance = None
    _model_name = "ProsusAI/finbert"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FinBERT, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
            
        logger.info("Loading FinBERT model (this may take a moment)...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self._model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self._model_name)
            
            # Use CPU for compatibility (and usually fast enough for batch inference on small text)
            self.nlp = pipeline("text-classification", model=self.model, tokenizer=self.tokenizer, return_all_scores=True)
            self.initialized = True
            logger.info("FinBERT loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load FinBERT: {e}")
            raise e

    def analyze_text(self, text: str) -> Dict[str, Union[str, float]]:
        """
        Analyze sentiment of a single text.
        Returns: {'label': 'positive'|'negative'|'neutral', 'score': float, 'detailed_scores': dict}
        """
        if not text or not text.strip():
            return {"label": "neutral", "score": 0.0}

        try:
            # Truncate to 512 tokens to match BERT limit
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            # Pipeline handles tokenization, but truncating before ensures we don't crash on raw text
            # Actually pipeline handles it if we pass truncation=True
            
            # Predict
            results = self.nlp(text[:2000], truncation=True, max_length=512) # passed specific args to call
            # Output format: [[{'label': 'positive', 'score': 0.9}, ...]]
            
            scores = {item['label']: item['score'] for item in results[0]}
            predicted_label = max(scores, key=scores.get)
            
            return {
                "label": predicted_label,
                "score": scores[predicted_label],
                "detailed_scores": scores
            }
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return {"label": "error", "score": 0.0}

    def analyze_batch(self, texts: List[str]) -> Dict[str, Union[float, str]]:
        """
        Analyze a batch of texts and return aggregated sentiment metrics.
        Returns: {'sentiment_score': float (-1 to 1), 'label': str, 'confidence': float}
        """
        if not texts:
            return {"sentiment_score": 0.0, "label": "neutral"}
            
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            return {"sentiment_score": 0.0, "label": "neutral"}
            
        results = []
        try:
            # Analyze each text
            # For massive batches we'd do use the pipe iterator, but for researching news 10-20 items is fine loop
            for text in valid_texts:
                results.append(self.analyze_text(text))
                
            # Aggregate
            # Mapping: positive=1, neutral=0, negative=-1
            # We weight by confidence score
            weighted_sum = 0.0
            total_weight = 0.0
            
            limit = len(results)
            pos_count = 0
            neg_count = 0
            neu_count = 0
            
            for res in results:
                label = res['label']
                score = res['score']
                
                weight = score 
                val = 0
                if label == 'positive': 
                    val = 1
                    pos_count += 1
                elif label == 'negative': 
                    val = -1
                    neg_count += 1
                else:
                    neu_count += 1
                    
                weighted_sum += val * weight
                total_weight += weight
                
            if total_weight == 0:
                final_score = 0
            else:
                final_score = weighted_sum / len(valid_texts) # Average sentiment per article, roughly
                # Or weighted_sum / total_weight? 
                # Let's map strictly -1 to 1.
                # Simple average of vectors: (1*conf_pos + -1*conf_neg + 0*conf_neu) / N
                # If we have 1 strong positive (0.9) and 1 strong negative (0.9), sum is 0. 
                
                final_score = 0
                for res in results:
                    s = res['score']
                    if res['label'] == 'positive': final_score += s
                    elif res['label'] == 'negative': final_score -= s
                final_score /= len(valid_texts)

            # Determine aggregate label
            if final_score > 0.15: agg_label = "bullish"
            elif final_score < -0.15: agg_label = "bearish"
            else: agg_label = "neutral"
            
            return {
                "sentiment_score": round(final_score, 2), # -1 to 1
                "label": agg_label,
                "article_count": len(valid_texts),
                "distribution": {"positive": pos_count, "negative": neg_count, "neutral": neu_count}
            }
            
        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            return {"sentiment_score": 0.0, "label": "error"}
