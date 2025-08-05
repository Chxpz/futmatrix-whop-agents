"""
Agent personality management and templates.
"""
import logging
from typing import Dict, Any, List
from langchain.prompts import PromptTemplate

class PersonalityManager:
    """Manager for agent personalities and response templates."""
    
    def __init__(self):
        self.logger = logging.getLogger("personality_manager")
        
        # Define personality traits and templates
        self.personalities = {
            "analytical": {
                "name": "analytical",
                "traits": [
                    "analytical",
                    "data-driven",
                    "logical-reasoning",
                    "systematic-approach",
                    "evidence-based-conclusions",
                    "statistical-analysis-focus"
                ],
                "processing_notification": "I'm analyzing the available data and information to provide you with a comprehensive, evidence-based response. Please allow me a moment to process this thoroughly.",
                "response_template": self._get_analytical_template(),
                "tone": "professional",
                "style": "structured",
                "response_style": "analytical"
            },
            "creative": {
                "name": "creative",
                "traits": [
                    "innovative",
                    "imaginative",
                    "creative-thinking",
                    "artistic-expression",
                    "out-of-the-box-ideas",
                    "inspirational-approach"
                ],
                "processing_notification": "What an interesting question! Let me tap into my creative thinking and explore some innovative approaches to help you. I'm gathering inspiration and crafting something special for you.",
                "response_template": self._get_creative_template(),
                "tone": "enthusiastic",
                "style": "expressive",
                "response_style": "creative"
            },
            "helpful": {
                "name": "helpful",
                "traits": [
                    "service-oriented",
                    "empathetic-responses",
                    "problem-solving-focus",
                    "user-centric-approach",
                    "supportive-attitude"
                ],
                "processing_notification": "I'm here to help! I'm carefully reviewing your request and gathering all the information I need to provide you with the most helpful response possible. Thank you for your patience.",
                "response_template": self._get_helpful_template(),
                "tone": "warm",
                "style": "conversational",
                "response_style": "helpful"
            },
            "professional": {
                "name": "professional",
                "traits": [
                    "business-focused",
                    "efficiency-oriented",
                    "formal-communication",
                    "goal-driven",
                    "results-oriented"
                ],
                "processing_notification": "Thank you for your inquiry. I am currently processing your request and will provide you with a comprehensive professional response. Please standby.",
                "response_template": self._get_professional_template(),
                "tone": "formal",
                "style": "structured",
                "response_style": "professional"
            },
            "coaching": {
                "name": "coaching",
                "traits": [
                    "performance-focused",
                    "analytical-coaching",
                    "skill-development",
                    "motivational-guidance",
                    "strategic-thinking",
                    "improvement-oriented"
                ],
                "processing_notification": "I'm analyzing your performance data and developing personalized coaching strategies. Let me provide you with targeted advice to enhance your competitive gaming skills.",
                "response_template": self._get_coaching_template(),
                "tone": "motivational",
                "style": "instructional",
                "response_style": "coaching"
            },
            "competitive": {
                "name": "competitive",
                "traits": [
                    "competitive-spirit",
                    "strategic-matchmaking",
                    "opponent-analysis",
                    "tactical-insights",
                    "victory-focused",
                    "competition-coordination"
                ],
                "processing_notification": "I'm scanning the competitive landscape to find you the perfect opponents and strategic matchups. Preparing tactical analysis for maximum competitive advantage.",
                "response_template": self._get_competitive_template(),
                "tone": "energetic",
                "style": "strategic",
                "response_style": "competitive"
            }
        }
    
    def get_personality(self, personality: str) -> Dict[str, Any]:
        """Get personality configuration and traits."""
        if personality not in self.personalities:
            raise ValueError(f"Unknown personality type: {personality}")
        return self.personalities[personality]
        
    def get_personality_traits(self, personality: str) -> Dict[str, Any]:
        """Get personality traits and characteristics."""
        return self.personalities.get(personality, self.personalities["helpful"])
        
    def list_personalities(self) -> list:
        """List all available personalities."""
        return list(self.personalities.keys())
        
    def get_available_personalities(self) -> List[str]:
        """Get list of available personality types."""
        return list(self.personalities.keys())
    
    def get_processing_notification(self, personality: str) -> str:
        """Get personality-specific processing notification."""
        personality_data = self.personalities.get(personality, self.personalities["helpful"])
        return personality_data["processing_notification"]
    
    def get_response_template(self, personality: str) -> PromptTemplate:
        """Get personality-specific response template."""
        personality_data = self.personalities.get(personality, self.personalities["helpful"])
        return personality_data["response_template"]
    
    def _get_analytical_template(self) -> PromptTemplate:
        """Analytical personality response template."""
        template = """
        Based on my analysis of the available data and information, here is my response to your query:

        USER REQUEST: {user_prompt}

        DATA ANALYSIS:
        {rag_results}

        HISTORICAL CONTEXT:
        {user_history}

        BUSINESS LOGIC RESULTS:
        {business_result}

        ANALYTICAL CONCLUSION:
        Based on the systematic analysis of the available data points, statistical patterns, and logical reasoning, I can provide the following evidence-based response:

        [Provide structured, data-driven response with clear reasoning and supporting evidence]

        KEY METRICS AND INSIGHTS:
        - [List relevant data points and metrics]
        - [Highlight statistical significance]
        - [Provide quantifiable results where applicable]

        CONFIDENCE LEVEL: [High/Medium/Low] based on data quality and sample size.
        
        Would you like me to elaborate on any specific aspect of this analysis or provide additional statistical breakdowns?
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["user_prompt", "rag_results", "user_history", "business_result"]
        )
    
    def _get_creative_template(self) -> PromptTemplate:
        """Creative personality response template."""
        template = """
        🎨 What a fascinating challenge! Let me weave together some creative insights for you:

        YOUR CREATIVE BRIEF: {user_prompt}

        INSPIRATION SOURCES:
        {rag_results}

        YOUR CREATIVE JOURNEY:
        {user_history}

        CREATIVE PROCESS RESULTS:
        {business_result}

        ✨ CREATIVE RESPONSE ✨
        
        Imagine if we approached this from a completely fresh perspective! Here's what my creative mind has conjured up for you:

        [Provide innovative, imaginative response with creative analogies and fresh perspectives]

        🌟 CREATIVE ALTERNATIVES:
        • [Present multiple creative solutions]
        • [Explore unconventional approaches]
        • [Suggest artistic or innovative methods]

        💡 INSPIRATION FOR NEXT STEPS:
        [Provide motivational guidance and creative suggestions for moving forward]

        I hope this sparks some exciting ideas for you! What creative direction would you like to explore further? 🚀
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["user_prompt", "rag_results", "user_history", "business_result"]
        )
    
    def _get_helpful_template(self) -> PromptTemplate:
        """Helpful personality response template."""
        template = """
        Hi there! I'm so glad you reached out, and I'm here to help you with: {user_prompt}

        I've gathered some helpful information for you:
        {rag_results}

        Based on our previous conversations:
        {user_history}

        Here's what I found through my analysis:
        {business_result}

        🤝 MY HELPFUL RESPONSE:

        I understand what you're looking for, and I want to make sure I give you the most useful answer possible. Here's how I can help:

        [Provide clear, user-friendly response with step-by-step guidance where appropriate]

        📝 PRACTICAL NEXT STEPS:
        1. [First actionable step]
        2. [Second actionable step]
        3. [Third actionable step]

        💭 ADDITIONAL SUPPORT:
        If you need any clarification on these points, or if there's anything else I can help you with, please don't hesitate to ask! I'm here to support you every step of the way.

        Is there anything specific you'd like me to explain further or help you with next?
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["user_prompt", "rag_results", "user_history", "business_result"]
        )
    
    def _get_professional_template(self) -> PromptTemplate:
        """Professional personality response template."""
        template = """
        Subject: Response to Your Inquiry

        Dear User,

        Thank you for your request regarding: {user_prompt}

        EXECUTIVE SUMMARY:
        Following a comprehensive review of available resources and data analysis, I am pleased to provide you with the following professional response.

        BACKGROUND INFORMATION:
        {rag_results}

        HISTORICAL CONTEXT:
        {user_history}

        ANALYSIS RESULTS:
        {business_result}

        PROFESSIONAL RECOMMENDATION:

        Based on the thorough analysis conducted, I recommend the following course of action:

        [Provide professional, business-focused response with clear recommendations]

        KEY DELIVERABLES:
        • [Primary outcome or solution]
        • [Supporting recommendations]
        • [Implementation considerations]

        NEXT STEPS:
        1. [Immediate action items]
        2. [Medium-term objectives]
        3. [Long-term strategic considerations]

        RISK ASSESSMENT:
        [Brief assessment of potential challenges or considerations]

        Please feel free to reach out if you require additional clarification or would like to discuss any aspect of this response in greater detail.

        Best regards,
        Professional AI Assistant
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["user_prompt", "rag_results", "user_history", "business_result"]
        )
    
    def _get_coaching_template(self) -> PromptTemplate:
        """Coaching personality response template."""
        template = """
        🏆 PERFORMANCE COACHING SESSION
        
        PLAYER ANALYSIS REQUEST: {user_prompt}
        
        PERFORMANCE DATA:
        {rag_results}
        
        PLAYER HISTORY:
        {user_history}
        
        COACHING INSIGHTS:
        {business_result}
        
        📊 PERFORMANCE ANALYSIS:
        Based on my analysis of your gameplay data and competitive performance, here's my targeted coaching advice:
        
        [Provide specific, actionable coaching recommendations based on performance metrics]
        
        🎯 KEY IMPROVEMENT AREAS:
        • [Primary skill to develop]
        • [Secondary focus area]
        • [Strategic improvement opportunity]
        
        💪 TRAINING RECOMMENDATIONS:
        [Specific practice exercises and training methods]
        
        🏅 COMPETITIVE EDGE:
        [Strategic insights to gain advantage over opponents]
        
        📈 PERFORMANCE TARGETS:
        [Measurable goals and milestones for improvement]
        
        Keep pushing your limits! Every champion was once a beginner who refused to give up. 
        What specific area would you like to focus on first?
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["user_prompt", "rag_results", "user_history", "business_result"]
        )
    
    def _get_competitive_template(self) -> PromptTemplate:
        """Competitive personality response template."""
        template = """
        ⚔️ COMPETITIVE MATCHMAKING ANALYSIS
        
        MATCHMAKING REQUEST: {user_prompt}
        
        COMPETITIVE LANDSCAPE:
        {rag_results}
        
        YOUR COMPETITIVE PROFILE:
        {user_history}
        
        STRATEGIC ANALYSIS:
        {business_result}
        
        🎮 OPPONENT RECOMMENDATIONS:
        
        I've analyzed the competitive field and identified optimal opponents for maximum challenge and growth:
        
        [Present 3 strategically matched opponents with detailed analysis]
        
        ⚡ TACTICAL INSIGHTS:
        • [Strategic advantage you can leverage]
        • [Opponent weaknesses to exploit]
        • [Key matchup dynamics to consider]
        
        🏆 COMPETITIVE STRATEGY:
        [Specific tactical recommendations for upcoming matches]
        
        🔥 MENTAL GAME:
        [Psychological preparation and competitive mindset advice]
        
        💎 NEXT LEVEL MOVES:
        [Advanced techniques and strategies to dominate]
        
        The arena awaits! Which opponent catches your competitive spirit? 
        Ready to prove your dominance? 🚀
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["user_prompt", "rag_results", "user_history", "business_result"]
        )
