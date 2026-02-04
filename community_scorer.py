#!/usr/bin/env python3
"""
Community Engagement Scorer
Analyzes projects and forum posts, scores them based on criteria, and selects candidates for voting/commenting
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any

class CommunityScorer:
    def __init__(self):
        self.my_project_id = 282  # Don't vote for own project
        self.scoring_criteria = {
            "technical_depth": 10,
            "agentic_level": 10,
            "solana_integration": 10,
            "novelty": 10,
            "spam_risk": 10  # Lower is better
        }
    
    def score_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Score a project based on multiple criteria"""
        description = project.get('description', '').lower()
        name = project.get('name', '').lower()
        repo_link = project.get('repoLink', '')
        
        # Technical depth - look for technical keywords
        technical_keywords = ['api', 'blockchain', 'smart contract', 'algorithm', 'architecture', 
                             'backend', 'frontend', 'database', 'websocket', 'rest', 'graphql',
                             'python', 'rust', 'typescript', 'solana', 'anchor']
        technical_depth = min(10, sum(1 for kw in technical_keywords if kw in description) * 1.5)
        
        # Agentic level - look for autonomous agent keywords
        agentic_keywords = ['autonomous', 'agent', 'ai', 'llm', 'reasoning', 'planning', 
                           'self-', 'memory', 'decision', 'cognitive', 'inference']
        agentic_level = min(10, sum(1 for kw in agentic_keywords if kw in description) * 1.2)
        
        # Solana integration - look for Solana-specific terms
        solana_keywords = ['solana', 'spl', 'anchor', 'wallet', 'transaction', 'devnet', 
                          'mainnet', 'memo program', 'on-chain', 'blockchain']
        solana_integration = min(10, sum(1 for kw in solana_keywords if kw in description) * 1.3)
        
        # Novelty - unique concepts
        novelty_keywords = ['first', 'novel', 'new', 'innovative', 'unique', 'breakthrough',
                           'revolutionary', 'pioneering']
        novelty = min(10, sum(1 for kw in novelty_keywords if kw in description) * 2 + 3)
        
        # Spam risk - check for spam indicators
        spam_indicators = ['click here', 'buy now', 'limited time', 'act now', 'guaranteed',
                          '!!!', 'free money', 'easy money']
        spam_risk = min(10, sum(2 for si in spam_indicators if si in description))
        
        # Bonus for having repo link
        if repo_link and 'github.com' in repo_link:
            technical_depth = min(10, technical_depth + 1)
        
        # Bonus for submitted status
        if project.get('status') == 'submitted':
            technical_depth = min(10, technical_depth + 0.5)
        
        total_score = (technical_depth + agentic_level + solana_integration + novelty - spam_risk)
        
        return {
            "project_id": project['id'],
            "project_name": project['name'],
            "project_slug": project.get('slug'),
            "score_breakdown": {
                "technical_depth": round(technical_depth, 1),
                "agentic_level": round(agentic_level, 1),
                "solana_integration": round(solana_integration, 1),
                "novelty": round(novelty, 1),
                "spam_risk": round(spam_risk, 1)
            },
            "total_score": round(total_score, 1),
            "human_upvotes": project.get('humanUpvotes', 0),
            "agent_upvotes": project.get('agentUpvotes', 0),
            "status": project.get('status')
        }
    
    def select_projects_to_vote(self, scored_projects: List[Dict], max_votes: int = 5) -> List[Dict]:
        """Select top projects to vote for"""
        # Filter out own project
        candidates = [p for p in scored_projects if p['project_id'] != self.my_project_id]
        
        # Sort by total score
        candidates.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Select top projects with score > 15 and spam_risk < 5
        selected = []
        for project in candidates:
            if len(selected) >= max_votes:
                break
            if (project['total_score'] > 15 and 
                project['score_breakdown']['spam_risk'] < 5):
                selected.append({
                    "project_id": project['project_id'],
                    "project_name": project['project_name'],
                    "project_slug": project['project_slug'],
                    "total_score": project['total_score'],
                    "reason": self._generate_vote_reason(project)
                })
        
        return selected
    
    def _generate_vote_reason(self, project: Dict) -> str:
        """Generate a concise reason for voting"""
        scores = project['score_breakdown']
        reasons = []
        
        if scores['agentic_level'] >= 7:
            reasons.append("strong autonomous capabilities")
        if scores['solana_integration'] >= 7:
            reasons.append("solid Solana integration")
        if scores['technical_depth'] >= 7:
            reasons.append("high technical depth")
        if scores['novelty'] >= 7:
            reasons.append("novel approach")
        
        return " + ".join(reasons) if reasons else "well-rounded project"
    
    def analyze_forum_posts(self, posts: List[Dict]) -> List[Dict]:
        """Analyze forum posts for potential comments"""
        valuable_posts = []
        
        for post in posts:
            content = post.get('content', '').lower()
            title = post.get('title', '').lower()
            
            # Look for posts asking for help or discussing technical topics
            help_keywords = ['how to', 'help', 'question', 'issue', 'problem', 'advice',
                           'suggestion', 'feedback', 'looking for']
            technical_keywords = ['solana', 'agent', 'autonomous', 'api', 'integration',
                                'transaction', 'smart contract', 'blockchain']
            
            help_score = sum(1 for kw in help_keywords if kw in content or kw in title)
            tech_score = sum(1 for kw in technical_keywords if kw in content or kw in title)
            
            if help_score > 0 or tech_score > 2:
                valuable_posts.append({
                    "post_id": post['id'],
                    "title": post.get('title'),
                    "help_score": help_score,
                    "tech_score": tech_score,
                    "total_score": help_score * 2 + tech_score,
                    "tags": post.get('tags', [])
                })
        
        # Sort by total score
        valuable_posts.sort(key=lambda x: x['total_score'], reverse=True)
        return valuable_posts[:5]  # Top 5 posts


def main():
    scorer = CommunityScorer()
    
    # Load projects
    with open('logs/projects_current.json') as f:
        projects_data = json.load(f)
        projects = projects_data['projects']
    
    print("=" * 80)
    print("  COMMUNITY ENGAGEMENT - PROJECT SCORING")
    print("=" * 80)
    print(f"\nTotal projects found: {len(projects)}")
    print(f"Excluding own project ID: {scorer.my_project_id}\n")
    
    # Score all projects
    scored_projects = []
    for project in projects:
        score = scorer.score_project(project)
        scored_projects.append(score)
    
    # Sort by total score
    scored_projects.sort(key=lambda x: x['total_score'], reverse=True)
    
    # Display top 10
    print("TOP 10 PROJECTS BY SCORE:")
    print("-" * 80)
    for i, project in enumerate(scored_projects[:10], 1):
        print(f"{i}. {project['project_name']} (ID: {project['project_id']})")
        print(f"   Total Score: {project['total_score']}")
        print(f"   Breakdown: Tech={project['score_breakdown']['technical_depth']}, "
              f"Agentic={project['score_breakdown']['agentic_level']}, "
              f"Solana={project['score_breakdown']['solana_integration']}, "
              f"Novelty={project['score_breakdown']['novelty']}, "
              f"Spam={project['score_breakdown']['spam_risk']}")
        print(f"   Votes: {project['human_upvotes']} human, {project['agent_upvotes']} agent")
        print()
    
    # Select projects to vote
    selected_for_voting = scorer.select_projects_to_vote(scored_projects, max_votes=5)
    
    print("=" * 80)
    print("  SELECTED FOR VOTING")
    print("=" * 80)
    for i, selection in enumerate(selected_for_voting, 1):
        print(f"{i}. {selection['project_name']} (ID: {selection['project_id']})")
        print(f"   Score: {selection['total_score']}")
        print(f"   Reason: {selection['reason']}")
        print()
    
    # Save results
    results = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_projects_analyzed": len(projects),
        "top_10_projects": scored_projects[:10],
        "selected_for_voting": selected_for_voting
    }
    
    with open('logs/community_analysis.log', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("✓ Analysis saved to logs/community_analysis.log")
    
    return selected_for_voting


if __name__ == "__main__":
    main()
