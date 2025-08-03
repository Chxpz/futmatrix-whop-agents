#!/usr/bin/env python3
"""
Unit tests for personality system.
"""
import pytest
from agents.personalities import PersonalityManager

class TestPersonalities:
    """Test personality management functionality."""
    
    @pytest.fixture
    def personality_manager(self):
        """Create personality manager instance."""
        return PersonalityManager()
    
    def test_get_analytical_personality(self, personality_manager):
        """Test analytical personality configuration."""
        personality = personality_manager.get_personality("analytical")
        
        assert personality is not None
        assert personality["name"] == "analytical"
        assert "traits" in personality
        assert "response_style" in personality
        assert "analytical" in personality["traits"]
        assert "data-driven" in personality["traits"]
    
    def test_get_creative_personality(self, personality_manager):
        """Test creative personality configuration."""
        personality = personality_manager.get_personality("creative")
        
        assert personality is not None
        assert personality["name"] == "creative"
        assert "traits" in personality
        assert "response_style" in personality
        assert "innovative" in personality["traits"]
        assert "imaginative" in personality["traits"]
    
    def test_get_helpful_personality(self, personality_manager):
        """Test helpful personality configuration."""
        personality = personality_manager.get_personality("helpful")
        
        assert personality is not None
        assert personality["name"] == "helpful"
        assert "traits" in personality
        assert "service-oriented" in personality["traits"]
    
    def test_get_professional_personality(self, personality_manager):
        """Test professional personality configuration."""
        personality = personality_manager.get_personality("professional")
        
        assert personality is not None
        assert personality["name"] == "professional"
        assert "traits" in personality
        assert "business-focused" in personality["traits"]
    
    def test_invalid_personality(self, personality_manager):
        """Test handling of invalid personality type."""
        with pytest.raises(ValueError):
            personality_manager.get_personality("invalid_personality")
    
    def test_list_available_personalities(self, personality_manager):
        """Test listing all available personalities."""
        personalities = personality_manager.list_personalities()
        
        expected_personalities = ["analytical", "creative", "helpful", "professional"]
        assert len(personalities) == len(expected_personalities)
        for personality_name in expected_personalities:
            assert personality_name in personalities
    
    def test_personality_response_templates(self, personality_manager):
        """Test that personalities have proper response templates."""
        for personality_name in ["analytical", "creative", "helpful", "professional"]:
            personality = personality_manager.get_personality(personality_name)
            assert "response_template" in personality
            assert personality["response_template"] is not None