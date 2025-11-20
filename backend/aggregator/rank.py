from typing import List, Dict
import re

class ResponseRanker:
    @staticmethod
    def rank_responses(responses: Dict[str, str]) -> List[str]:
        """Rank responses by quality indicators"""
        scored_responses = []
        
        for provider, response in responses.items():
            score = 0
            
            # Length scoring (moderate length is better)
            length = len(response.split())
            if 50 <= length <= 300:
                score += 2
            elif length > 300:
                score += 1
            
            # Structure scoring
            if any(marker in response.lower() for marker in ["first", "second", "third", "finally", "in conclusion"]):
                score += 1
            
            # Question answering indicators
            if any(marker in response.lower() for marker in ["based on", "according to", "research shows"]):
                score += 1
            
            # Clarity indicators
            sentence_count = len(re.findall(r'[.!?]+', response))
            if sentence_count >= 3:
                score += 1
            
            scored_responses.append((provider, response, score))
        
        # Sort by score descending
        scored_responses.sort(key=lambda x: x[2], reverse=True)
        return [resp[1] for resp in scored_responses]