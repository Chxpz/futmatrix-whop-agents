"""
Business rules engine for different agent specializations.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from utils.exceptions import BusinessRuleError

class BusinessRuleEngine:
    """Engine for processing business logic based on agent specialization."""
    
    def __init__(self):
        self.logger = logging.getLogger("business_rules")
        
        # Define business rule processors
        self.rule_processors = {
            "financial_advisor": self._process_financial_advisor_rules,
            "content_creator": self._process_content_creator_rules,
            "technical_support": self._process_technical_support_rules,
            "general_assistant": self._process_general_assistant_rules
        }
    
    async def process(
        self,
        business_rule_type: str,
        prompt: str,
        context: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Process business rules based on agent type."""
        try:
            processor = self.rule_processors.get(business_rule_type)
            
            if not processor:
                self.logger.warning(f"Unknown business rule type: {business_rule_type}")
                return await self._process_general_assistant_rules(prompt, context, user_id)
            
            result = await processor(prompt, context, user_id)
            
            # Add processing metadata
            result["processing_metadata"] = {
                "business_rule_type": business_rule_type,
                "processed_at": datetime.utcnow().isoformat(),
                "user_id": user_id
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing business rules: {e}")
            raise BusinessRuleError(f"Business rule processing failed: {e}")
    
    async def _process_financial_advisor_rules(
        self,
        prompt: str,
        context: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Process financial advisor specific business rules."""
        try:
            result = {
                "category": "financial_advice",
                "risk_assessment": self._assess_financial_risk(prompt),
                "compliance_check": self._check_financial_compliance(prompt),
                "market_context": self._get_market_context(),
                "recommendations": []
            }
            
            # Analyze prompt for financial keywords
            financial_keywords = [
                "investment", "portfolio", "stocks", "bonds", "retirement",
                "401k", "ira", "savings", "budget", "debt", "mortgage",
                "insurance", "tax", "planning", "fund", "dividend"
            ]
            
            detected_keywords = [kw for kw in financial_keywords if kw.lower() in prompt.lower()]
            result["detected_topics"] = detected_keywords
            
            # Generate specific recommendations based on detected topics
            if "investment" in detected_keywords or "portfolio" in detected_keywords:
                result["recommendations"].append({
                    "type": "investment_advice",
                    "priority": "high",
                    "message": "Consider diversification across asset classes and risk tolerance alignment"
                })
            
            if "retirement" in detected_keywords:
                result["recommendations"].append({
                    "type": "retirement_planning",
                    "priority": "high",
                    "message": "Review contribution limits and employer matching opportunities"
                })
            
            if "debt" in detected_keywords:
                result["recommendations"].append({
                    "type": "debt_management",
                    "priority": "medium",
                    "message": "Consider debt consolidation and payment prioritization strategies"
                })
            
            # Add user history context if available
            user_history = context.get("user_history", [])
            if user_history:
                result["user_context"] = self._analyze_financial_history(user_history)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in financial advisor rules: {e}")
            return {"category": "financial_advice", "error": str(e)}
    
    async def _process_content_creator_rules(
        self,
        prompt: str,
        context: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Process content creator specific business rules."""
        try:
            result = {
                "category": "content_creation",
                "content_type": self._identify_content_type(prompt),
                "target_audience": self._analyze_target_audience(prompt),
                "tone_analysis": self._analyze_desired_tone(prompt),
                "seo_keywords": self._extract_seo_keywords(prompt),
                "creative_suggestions": []
            }
            
            # Content type specific processing
            content_type = result["content_type"]
            
            if content_type == "blog_post":
                result["creative_suggestions"].extend([
                    "Consider adding personal anecdotes for engagement",
                    "Include relevant statistics and data points",
                    "Add call-to-action at the end"
                ])
            
            elif content_type == "social_media":
                result["creative_suggestions"].extend([
                    "Keep it concise and visually appealing",
                    "Include relevant hashtags",
                    "Consider platform-specific formatting"
                ])
            
            elif content_type == "marketing":
                result["creative_suggestions"].extend([
                    "Focus on benefits over features",
                    "Include social proof if available",
                    "Create urgency or scarcity when appropriate"
                ])
            
            # Analyze user history for content patterns
            user_history = context.get("user_history", [])
            if user_history:
                result["content_patterns"] = self._analyze_content_history(user_history)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in content creator rules: {e}")
            return {"category": "content_creation", "error": str(e)}
    
    async def _process_technical_support_rules(
        self,
        prompt: str,
        context: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Process technical support specific business rules."""
        try:
            result = {
                "category": "technical_support",
                "issue_type": self._classify_technical_issue(prompt),
                "urgency_level": self._assess_technical_urgency(prompt),
                "troubleshooting_steps": [],
                "escalation_needed": False,
                "resources": []
            }
            
            issue_type = result["issue_type"]
            
            # Define troubleshooting steps based on issue type
            troubleshooting_map = {
                "connectivity": [
                    "Check internet connection",
                    "Restart router/modem",
                    "Test with different device",
                    "Check firewall settings"
                ],
                "software": [
                    "Restart the application",
                    "Check for updates",
                    "Clear cache and temporary files",
                    "Run in safe mode"
                ],
                "hardware": [
                    "Check all cable connections",
                    "Restart the device",
                    "Check for overheating",
                    "Run hardware diagnostics"
                ],
                "performance": [
                    "Check system resources",
                    "Close unnecessary programs",
                    "Scan for malware",
                    "Update drivers"
                ]
            }
            
            result["troubleshooting_steps"] = troubleshooting_map.get(issue_type, [
                "Gather more information about the issue",
                "Document error messages",
                "Try basic restart procedures"
            ])
            
            # Determine if escalation is needed
            escalation_keywords = ["critical", "urgent", "production", "down", "crashed", "security"]
            if any(keyword in prompt.lower() for keyword in escalation_keywords):
                result["escalation_needed"] = True
                result["escalation_reason"] = "Critical issue detected requiring immediate attention"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in technical support rules: {e}")
            return {"category": "technical_support", "error": str(e)}
    
    async def _process_general_assistant_rules(
        self,
        prompt: str,
        context: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Process general assistant business rules."""
        try:
            result = {
                "category": "general_assistance",
                "intent": self._classify_general_intent(prompt),
                "complexity": self._assess_query_complexity(prompt),
                "response_type": "informational",
                "follow_up_suggestions": []
            }
            
            # Generate follow-up suggestions based on intent
            intent = result["intent"]
            
            if intent == "question":
                result["follow_up_suggestions"] = [
                    "Would you like more detailed information?",
                    "Are there related topics you'd like to explore?",
                    "Do you need help with implementation?"
                ]
            elif intent == "task":
                result["follow_up_suggestions"] = [
                    "Would you like step-by-step guidance?",
                    "Do you need help breaking this down further?",
                    "Are there any constraints I should consider?"
                ]
            elif intent == "problem":
                result["follow_up_suggestions"] = [
                    "Would you like alternative solutions?",
                    "Do you need help prioritizing approaches?",
                    "Are there any resources you'd like me to recommend?"
                ]
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in general assistant rules: {e}")
            return {"category": "general_assistance", "error": str(e)}
    
    # Helper methods for business rule processing
    
    def _assess_financial_risk(self, prompt: str) -> str:
        """Assess financial risk level of the request."""
        high_risk_keywords = ["day trading", "cryptocurrency", "leverage", "margin", "options"]
        medium_risk_keywords = ["stocks", "mutual funds", "etf", "investment"]
        
        if any(keyword in prompt.lower() for keyword in high_risk_keywords):
            return "high"
        elif any(keyword in prompt.lower() for keyword in medium_risk_keywords):
            return "medium"
        else:
            return "low"
    
    def _check_financial_compliance(self, prompt: str) -> Dict[str, Any]:
        """Check financial compliance requirements."""
        return {
            "disclaimer_required": True,
            "fiduciary_warning": "not_investment_advice",
            "regulatory_notice": "Consult with a qualified financial advisor"
        }
    
    def _get_market_context(self) -> Dict[str, Any]:
        """Get current market context (simplified for MVP)."""
        return {
            "market_status": "normal_trading",
            "volatility_level": "moderate",
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _identify_content_type(self, prompt: str) -> str:
        """Identify the type of content being requested."""
        content_keywords = {
            "blog_post": ["blog", "article", "post", "write about"],
            "social_media": ["twitter", "facebook", "instagram", "social", "tweet", "post"],
            "marketing": ["marketing", "advertisement", "campaign", "promotion", "sales"],
            "email": ["email", "newsletter", "subject line"],
            "script": ["script", "video", "presentation", "speech"]
        }
        
        for content_type, keywords in content_keywords.items():
            if any(keyword in prompt.lower() for keyword in keywords):
                return content_type
        
        return "general_content"
    
    def _analyze_target_audience(self, prompt: str) -> str:
        """Analyze the target audience from the prompt."""
        audience_keywords = {
            "professionals": ["professional", "business", "corporate", "enterprise"],
            "consumers": ["customer", "consumer", "general public", "people"],
            "students": ["student", "education", "learning", "academic"],
            "technical": ["developer", "technical", "engineer", "IT"]
        }
        
        for audience, keywords in audience_keywords.items():
            if any(keyword in prompt.lower() for keyword in keywords):
                return audience
        
        return "general_audience"
    
    def _analyze_desired_tone(self, prompt: str) -> str:
        """Analyze the desired tone from the prompt."""
        tone_keywords = {
            "formal": ["formal", "professional", "business"],
            "casual": ["casual", "friendly", "relaxed", "informal"],
            "persuasive": ["convince", "persuade", "sell", "promote"],
            "educational": ["explain", "teach", "inform", "educate"]
        }
        
        for tone, keywords in tone_keywords.items():
            if any(keyword in prompt.lower() for keyword in keywords):
                return tone
        
        return "neutral"
    
    def _extract_seo_keywords(self, prompt: str) -> list[str]:
        """Extract potential SEO keywords from the prompt."""
        # Simple keyword extraction (in production, use more sophisticated NLP)
        words = prompt.lower().split()
        
        # Filter out common stop words
        stop_words = {"the", "is", "at", "which", "on", "a", "an", "and", "or", "but", "in", "with", "to", "for", "of", "as", "by"}
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        return keywords[:5]  # Return top 5 potential keywords
    
    def _classify_technical_issue(self, prompt: str) -> str:
        """Classify the type of technical issue."""
        issue_keywords = {
            "connectivity": ["internet", "network", "connection", "wifi", "ethernet"],
            "software": ["application", "program", "software", "app", "error", "crash"],
            "hardware": ["hardware", "device", "computer", "laptop", "printer", "monitor"],
            "performance": ["slow", "performance", "speed", "lag", "freezing", "hanging"]
        }
        
        for issue_type, keywords in issue_keywords.items():
            if any(keyword in prompt.lower() for keyword in keywords):
                return issue_type
        
        return "general"
    
    def _assess_technical_urgency(self, prompt: str) -> str:
        """Assess the urgency level of a technical issue."""
        urgent_keywords = ["critical", "urgent", "down", "crashed", "not working", "broken"]
        medium_keywords = ["slow", "issue", "problem", "error"]
        
        if any(keyword in prompt.lower() for keyword in urgent_keywords):
            return "high"
        elif any(keyword in prompt.lower() for keyword in medium_keywords):
            return "medium"
        else:
            return "low"
    
    def _classify_general_intent(self, prompt: str) -> str:
        """Classify the general intent of the prompt."""
        question_words = ["what", "why", "how", "when", "where", "who", "which"]
        task_words = ["help", "create", "make", "build", "generate", "write"]
        problem_words = ["problem", "issue", "trouble", "fix", "solve", "error"]
        
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in question_words):
            return "question"
        elif any(word in prompt_lower for word in task_words):
            return "task"
        elif any(word in prompt_lower for word in problem_words):
            return "problem"
        else:
            return "general"
    
    def _assess_query_complexity(self, prompt: str) -> str:
        """Assess the complexity of the query."""
        # Simple complexity assessment based on length and keywords
        word_count = len(prompt.split())
        
        complex_indicators = ["multiple", "various", "complex", "detailed", "comprehensive"]
        
        if word_count > 50 or any(indicator in prompt.lower() for indicator in complex_indicators):
            return "high"
        elif word_count > 20:
            return "medium"
        else:
            return "low"
    
    def _analyze_financial_history(self, user_history: list[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user's financial query history."""
        # Simplified analysis for MVP
        return {
            "previous_topics": ["investment", "retirement"],  # Would be extracted from history
            "risk_profile": "moderate",  # Would be inferred from history
            "engagement_level": "active"  # Based on interaction frequency
        }
    
    def _analyze_content_history(self, user_history: list[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user's content creation history."""
        # Simplified analysis for MVP
        return {
            "preferred_formats": ["blog_post", "social_media"],  # Would be extracted from history
            "content_themes": ["technology", "business"],  # Would be inferred from history
            "engagement_patterns": "regular_creator"  # Based on interaction frequency
        }
