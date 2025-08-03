#!/usr/bin/env python3
"""
Unit tests for business rules engine.
"""
import pytest
import asyncio
from agents.business_rules import BusinessRuleEngine

class TestBusinessRules:
    """Test business rules engine functionality."""
    
    @pytest.fixture
    def business_engine(self):
        """Create business rules engine instance."""
        return BusinessRuleEngine()
    
    @pytest.mark.asyncio
    async def test_financial_advisor_rules(self, business_engine):
        """Test financial advisor business rules."""
        result = await business_engine.process(
            business_rule_type="financial_advisor",
            prompt="Should I invest in cryptocurrency?",
            context={},
            user_id="test_user"
        )
        
        assert result is not None
        assert "compliance_check" in result
        assert "risk_assessment" in result
        assert "user_analysis" in result
        assert result["compliance_check"]["passed"] is True
        assert result["risk_assessment"]["level"] in ["low", "medium", "high"]
    
    @pytest.mark.asyncio
    async def test_content_creator_rules(self, business_engine):
        """Test content creator business rules."""
        result = await business_engine.process(
            business_rule_type="content_creator",
            prompt="Create a social media post about technology",
            context={},
            user_id="test_user"
        )
        
        assert result is not None
        assert "content_moderation" in result
        assert "creativity_enhancement" in result
        assert "user_analysis" in result
        assert result["content_moderation"]["approved"] is True
        assert "guidelines" in result["creativity_enhancement"]
    
    @pytest.mark.asyncio
    async def test_technical_support_rules(self, business_engine):
        """Test technical support business rules."""
        result = await business_engine.process(
            business_rule_type="technical_support",
            prompt="How do I fix my computer issue?",
            context={},
            user_id="test_user"
        )
        
        assert result is not None
        assert "issue_categorization" in result
        assert "solution_priority" in result
        assert "user_analysis" in result
        assert result["issue_categorization"]["category"] in ["hardware", "software", "network", "general"]
    
    @pytest.mark.asyncio
    async def test_general_assistant_rules(self, business_engine):
        """Test general assistant business rules."""
        result = await business_engine.process(
            business_rule_type="general_assistant",
            prompt="Help me plan my day",
            context={},
            user_id="test_user"
        )
        
        assert result is not None
        assert "request_analysis" in result
        assert "assistance_level" in result
        assert "user_analysis" in result
        assert result["assistance_level"] == "comprehensive"
    
    @pytest.mark.asyncio
    async def test_invalid_business_rules(self, business_engine):
        """Test handling of invalid business rule type."""
        with pytest.raises(ValueError):
            await business_engine.process(
                business_rule_type="invalid_rule_type",
                prompt="Test prompt",
                context={},
                user_id="test_user"
            )
    
    @pytest.mark.asyncio
    async def test_business_rules_with_context(self, business_engine):
        """Test business rules processing with context."""
        context = {
            "previous_interactions": 5,
            "user_preferences": {"risk_tolerance": "moderate"}
        }
        
        result = await business_engine.process(
            business_rule_type="financial_advisor",
            prompt="What investment should I choose?",
            context=context,
            user_id="test_user"
        )
        
        assert result is not None
        assert "user_analysis" in result
        # Context should influence the analysis
        assert result["user_analysis"]["engagement_level"] == "active"