from typing import List, Dict
from backend.aggregator.rank import ResponseRanker

class Synthesizer:
    def __init__(self):
        self.ranker = ResponseRanker()
    
    def synthesize(self, responses: Dict[str, str]) -> str:
        """Synthesize multiple responses into one high-quality answer"""
        if not responses:
            return "No responses available from providers."
        
        # Rank responses by quality
        ranked_responses = self.ranker.rank_responses(responses)
        
        if not ranked_responses:
            return "Could not generate a synthesized response."
        
        # Use the highest-ranked response as base
        base_response = ranked_responses[0]
        
        # Add insights from other high-quality responses
        additional_insights = []
        for response in ranked_responses[1:2]:  # Take next best 1-2 responses
            unique_points = self._extract_unique_insights(response, base_response)
            if unique_points:
                additional_insights.extend(unique_points)
        
        # Construct final response
        synthesized = base_response
        
        if additional_insights:
            synthesized += "\n\nAdditionally: " + " ".join(additional_insights[:2])
        
        return synthesized
    
    def _extract_unique_insights(self, new_response: str, base_response: str) -> List[str]:
        """Extract unique insights not present in base response"""
        base_words = set(base_response.lower().split())
        new_words = set(new_response.lower().split())
        
        # Simple intersection check (could be enhanced with NLP)
        unique_words = new_words - base_words
        if len(unique_words) > 5:  # If significant new content
            sentences = new_response.split('.')
            unique_sentences = []
            for sentence in sentences:
                if len(sentence.strip()) > 20 and any(word in sentence.lower() for word in unique_words):
                    unique_sentences.append(sentence.strip())
            return unique_sentences[:2]  # Return max 2 unique sentences
        
        return []