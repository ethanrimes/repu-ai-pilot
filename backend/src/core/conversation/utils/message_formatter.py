# backend/src/core/conversation/utils/message_formatter.py

import re
from typing import Dict, Any, Optional

class MessageFormatter:
    """Utility class for formatting conversation messages for proper rendering"""
    
    @staticmethod
    def format_for_chat(text: str) -> str:
        """
        Format text for proper chat rendering with markdown support
        
        Args:
            text: Raw text content to format
            
        Returns:
            Properly formatted text for frontend rendering
        """
        # Normalize line breaks
        text = re.sub(r'\r\n|\r', '\n', text)
        
        # Ensure proper spacing around numbered lists
        text = re.sub(r'([^\n])\n(\d+\.)', r'\1\n\n\2', text)
        
        # Ensure proper spacing after colons that precede lists
        text = re.sub(r'([:])\n(\d+\.)', r'\1\n\n\2', text)
        
        # Ensure proper spacing around headings
        text = re.sub(r'([^\n])\n(#+\s)', r'\1\n\n\2', text)
        text = re.sub(r'(#+\s[^\n]+)\n([^\n])', r'\1\n\n\2', text)
        
        # Ensure proper spacing around bold text blocks
        text = re.sub(r'([^\n])\n(\*\*[^*]+\*\*)', r'\1\n\n\2', text)
        
        # Clean up excessive line breaks (more than 2 consecutive)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Ensure proper indentation for status indicators
        text = re.sub(r'\n   ([✅❌])', r'\n   \1', text)
        
        return text.strip()
    
    @staticmethod
    def format_list_items(items: list, numbered: bool = True) -> str:
        """
        Format a list of items with proper spacing
        
        Args:
            items: List of items to format
            numbered: Whether to use numbered list (1. 2. 3.) or bullet points
            
        Returns:
            Formatted list string
        """
        formatted_items = []
        
        for i, item in enumerate(items, 1):
            if numbered:
                prefix = f"{i}. "
            else:
                prefix = "• "
            
            formatted_items.append(f"{prefix}{item}")
        
        return "\n".join(formatted_items)
    
    @staticmethod
    def add_emphasis(text: str, style: str = "bold") -> str:
        """
        Add markdown emphasis to text
        
        Args:
            text: Text to emphasize
            style: Style type ('bold', 'italic', 'code')
            
        Returns:
            Text with markdown emphasis
        """
        if style == "bold":
            return f"**{text}**"
        elif style == "italic":
            return f"*{text}*"
        elif style == "code":
            return f"`{text}`"
        else:
            return text
    
    @staticmethod
    def create_section(title: str, content: str, level: int = 2) -> str:
        """
        Create a markdown section with title and content
        
        Args:
            title: Section title
            content: Section content
            level: Heading level (1-6)
            
        Returns:
            Formatted section string
        """
        heading_prefix = "#" * level
        return f"{heading_prefix} {title}\n\n{content}"
    
    @staticmethod
    def ensure_markdown_compatibility(text: str) -> str:
        """
        Ensure text is compatible with markdown renderers
        
        Args:
            text: Text to make markdown-compatible
            
        Returns:
            Markdown-compatible text
        """
        # Escape characters that might conflict with markdown if they're not intentional
        # This is conservative - only escape things that are clearly not intentional markdown
        
        # Don't escape asterisks that are clearly for bold/italic
        # Don't escape hashes that are clearly for headers
        # Don't escape backticks that are clearly for code
        
        # Just ensure proper spacing and line breaks
        return MessageFormatter.format_for_chat(text)
