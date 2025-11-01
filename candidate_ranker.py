import numpy as np
from typing import List, Dict

class CandidateRanker:
    def __init__(self):
        """Initialize candidate ranking system"""
        self.ranking_criteria = {
            'overallScore': 0.40,
            'skillsMatch': 0.25,
            'experienceMatch': 0.20,
            'educationMatch': 0.10,
            'semanticMatch': 0.05
        }
    
    def rank_candidates(self, candidates: List[Dict], custom_weights: Dict = None) -> List[Dict]:
        """
        Rank candidates based on match scores
        
        Args:
            candidates: List of candidate match results
            custom_weights: Optional custom ranking weights
        
        Returns:
            Sorted list of candidates with ranks
        """
        if not candidates:
            return []
        
        # Use custom weights if provided
        weights = custom_weights if custom_weights else self.ranking_criteria
        
        # Calculate composite scores
        for candidate in candidates:
            candidate['compositeScore'] = self._calculate_composite_score(candidate, weights)
            candidate['rank'] = 0  # Will be assigned after sorting
            candidate['tier'] = ''  # Will be assigned after sorting
        
        # Sort by composite score
        ranked_candidates = sorted(
            candidates,
            key=lambda x: x['compositeScore'],
            reverse=True
        )
        
        # Assign ranks and tiers
        for idx, candidate in enumerate(ranked_candidates):
            candidate['rank'] = idx + 1
            candidate['tier'] = self._assign_tier(candidate['compositeScore'])
            candidate['recommendation'] = self._generate_recommendation(candidate)
        
        return ranked_candidates
    
    def _calculate_composite_score(self, candidate: Dict, weights: Dict) -> float:
        """Calculate weighted composite score"""
        score = 0.0
        
        for criterion, weight in weights.items():
            if criterion in candidate:
                score += candidate[criterion] * weight
        
        return round(score, 2)
    
    def _assign_tier(self, score: float) -> str:
        """Assign tier based on composite score"""
        if score >= 85:
            return 'Excellent'
        elif score >= 70:
            return 'Strong'
        elif score >= 55:
            return 'Good'
        elif score >= 40:
            return 'Average'
        else:
            return 'Below Average'
    
    def _generate_recommendation(self, candidate: Dict) -> str:
        """Generate hiring recommendation"""
        score = candidate.get('compositeScore', 0)
        tier = candidate.get('tier', '')
        
        recommendations = {
            'Excellent': 'Highly Recommended - Schedule interview immediately',
            'Strong': 'Recommended - Strong candidate, proceed with interview',
            'Good': 'Consider - Good potential, review in detail',
            'Average': 'Maybe - Requires careful evaluation',
            'Below Average': 'Not Recommended - Significant skill gaps'
        }
        
        return recommendations.get(tier, 'Review required')
    
    def get_top_candidates(self, candidates: List[Dict], top_n: int = 10) -> List[Dict]:
        """Get top N candidates"""
        ranked = self.rank_candidates(candidates)
        return ranked[:top_n]
    
    def filter_by_threshold(self, candidates: List[Dict], threshold: float = 60.0) -> List[Dict]:
        """Filter candidates above threshold"""
        ranked = self.rank_candidates(candidates)
        return [c for c in ranked if c['compositeScore'] >= threshold]
    
    def compare_candidates(self, candidate1: Dict, candidate2: Dict) -> Dict:
        """Compare two candidates side by side"""
        comparison = {
            'candidate1': {
                'name': candidate1.get('candidateName'),
                'scores': {
                    'overall': candidate1.get('matchScore', 0),
                    'skills': candidate1.get('skillsMatch', 0),
                    'experience': candidate1.get('experienceMatch', 0),
                    'education': candidate1.get('educationMatch', 0)
                }
            },
            'candidate2': {
                'name': candidate2.get('candidateName'),
                'scores': {
                    'overall': candidate2.get('matchScore', 0),
                    'skills': candidate2.get('skillsMatch', 0),
                    'experience': candidate2.get('experienceMatch', 0),
                    'education': candidate2.get('educationMatch', 0)
                }
            },
            'winner': self._determine_winner(candidate1, candidate2),
            'insights': self._generate_comparison_insights(candidate1, candidate2)
        }
        
        return comparison
    
    def _determine_winner(self, candidate1: Dict, candidate2: Dict) -> str:
        """Determine which candidate is stronger"""
        score1 = candidate1.get('matchScore', 0)
        score2 = candidate2.get('matchScore', 0)
        
        if score1 > score2:
            return candidate1.get('candidateName', 'Candidate 1')
        elif score2 > score1:
            return candidate2.get('candidateName', 'Candidate 2')
        else:
            return 'Tie'
    
    def _generate_comparison_insights(self, candidate1: Dict, candidate2: Dict) -> List[str]:
        """Generate insights from comparison"""
        insights = []
        
        # Skills comparison
        if candidate1.get('skillsMatch', 0) > candidate2.get('skillsMatch', 0):
            insights.append(f"{candidate1.get('candidateName')} has better skills match")
        elif candidate2.get('skillsMatch', 0) > candidate1.get('skillsMatch', 0):
            insights.append(f"{candidate2.get('candidateName')} has better skills match")
        
        # Experience comparison
        if candidate1.get('experienceMatch', 0) > candidate2.get('experienceMatch', 0):
            insights.append(f"{candidate1.get('candidateName')} has more relevant experience")
        elif candidate2.get('experienceMatch', 0) > candidate1.get('experienceMatch', 0):
            insights.append(f"{candidate2.get('candidateName')} has more relevant experience")
        
        return insights
    
    def generate_diversity_score(self, candidates: List[Dict]) -> Dict:
        """Calculate diversity metrics for candidate pool"""
        if not candidates:
            return {}
        
        # This is a basic implementation
        # You can extend it with actual diversity metrics
        
        skill_diversity = self._calculate_skill_diversity(candidates)
        experience_range = self._calculate_experience_range(candidates)
        
        return {
            'skillDiversity': skill_diversity,
            'experienceRange': experience_range,
            'poolSize': len(candidates),
            'topTierCount': len([c for c in candidates if c.get('tier') == 'Excellent'])
        }
    
    def _calculate_skill_diversity(self, candidates: List[Dict]) -> float:
        """Calculate skill diversity in candidate pool"""
        all_skills = set()
        
        for candidate in candidates:
            matched_skills = candidate.get('matchedSkills', [])
            all_skills.update(matched_skills)
        
        # Return unique skill count
        return len(all_skills)
    
    def _calculate_experience_range(self, candidates: List[Dict]) -> Dict:
        """Calculate experience range distribution"""
        exp_scores = [c.get('experienceMatch', 0) for c in candidates]
        
        if not exp_scores:
            return {}
        
        return {
            'min': min(exp_scores),
            'max': max(exp_scores),
            'avg': round(np.mean(exp_scores), 2),
            'median': round(np.median(exp_scores), 2)
        }
    
    def get_ranking_insights(self, candidates: List[Dict]) -> Dict:
        """Generate insights about candidate ranking"""
        if not candidates:
            return {}
        
        ranked = self.rank_candidates(candidates)
        
        scores = [c['compositeScore'] for c in ranked]
        
        insights = {
            'totalCandidates': len(ranked),
            'averageScore': round(np.mean(scores), 2),
            'medianScore': round(np.median(scores), 2),
            'topScore': max(scores),
            'lowScore': min(scores),
            'excellentCount': len([c for c in ranked if c['tier'] == 'Excellent']),
            'strongCount': len([c for c in ranked if c['tier'] == 'Strong']),
            'goodCount': len([c for c in ranked if c['tier'] == 'Good']),
            'distribution': self._get_score_distribution(scores)
        }
        
        return insights
    
    def _get_score_distribution(self, scores: List[float]) -> Dict:
        """Get score distribution"""
        return {
            '90-100': len([s for s in scores if s >= 90]),
            '80-89': len([s for s in scores if 80 <= s < 90]),
            '70-79': len([s for s in scores if 70 <= s < 80]),
            '60-69': len([s for s in scores if 60 <= s < 70]),
            '50-59': len([s for s in scores if 50 <= s < 60]),
            'below-50': len([s for s in scores if s < 50])
        }