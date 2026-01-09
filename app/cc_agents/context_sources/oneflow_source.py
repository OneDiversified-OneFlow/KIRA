"""
OneFlow Data Context Source

Provides context from OneFlow data (tasks, projects, users) for enhanced context injection.
Initially uses mocked data; will be replaced with real API calls when endpoints are implemented.
"""

import logging
from typing import Optional, Dict, Any

from app.cc_agents.context_sources import ContextSource, ContextSourceError


class OneFlowContextSource(ContextSource):
    """
    Context source that retrieves context from OneFlow data.
    
    Initially uses mocked data. When OneFlow API endpoints are implemented
    (deferred per FR-027), this will make real API calls.
    """
    
    def __init__(self, api_key: Optional[str] = None, api_base_url: Optional[str] = None):
        """
        Initialize OneFlow context source.
        
        Args:
            api_key: OneFlow API key (optional, for future API integration)
            api_base_url: OneFlow API base URL (optional, for future API integration)
        """
        self._source_name = "oneflow"
        self._api_key = api_key
        self._api_base_url = api_base_url or "https://api.oneflow.example.com"  # Placeholder
        self._mocked = True  # Using mocked data initially
    
    async def get_context(
        self,
        search_query: str,
        slack_data: Optional[Dict[str, Any]] = None,
        message_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Retrieve context from OneFlow data.
        
        Currently returns mocked data. When API endpoints are implemented,
        this will make real API calls to fetch OneFlow tasks, projects, and users.
        
        Args:
            search_query: The search query or user message
            slack_data: Slack context data (channel, user, etc.)
            message_data: Current message data
            **kwargs: Additional parameters (ignored for now)
            
        Returns:
            str: Context string from OneFlow data. Empty string if no relevant data found.
        """
        if self._mocked:
            return self._get_mocked_context(search_query, slack_data, message_data)
        
        # TODO: Implement real API calls when endpoints are available
        # This will use the API contracts defined in:
        # specs/oneflow/001-fork-kira-repository/contracts/api-contracts.md
        try:
            # Future implementation:
            # context = await self._fetch_oneflow_api_context(search_query, slack_data, message_data)
            # return context
            pass
        except Exception as e:
            logging.error(f"[ONEFLOW_SOURCE] Error retrieving OneFlow context: {e}")
            return ""
    
    def _get_mocked_context(
        self,
        search_query: str,
        slack_data: Optional[Dict[str, Any]] = None,
        message_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get mocked OneFlow context for testing/development.
        
        Returns structured mock data that represents what OneFlow API would return.
        This allows development and testing to proceed before API endpoints are implemented.
        
        Args:
            search_query: The search query
            slack_data: Slack context data
            message_data: Current message data
            
        Returns:
            str: Mocked OneFlow context string
        """
        # Simple keyword-based mock responses
        query_lower = search_query.lower()
        
        context_parts = []
        
        # Mock tasks context
        if any(keyword in query_lower for keyword in ["task", "work", "todo", "progress"]):
            context_parts.append("## OneFlow Tasks (Mocked)")
            context_parts.append("- Task: Implement enhanced context injection (in-progress)")
            context_parts.append("- Task: Design persona system (pending)")
            context_parts.append("- Task: Create adapter layer (pending)")
        
        # Mock projects context
        if any(keyword in query_lower for keyword in ["project", "work item", "feature"]):
            context_parts.append("## OneFlow Projects (Mocked)")
            context_parts.append("- Project: KIRA Integration (active)")
            context_parts.append("- Project: Enhanced Context Injection (in-progress)")
        
        # Mock users context
        if any(keyword in query_lower for keyword in ["user", "team", "person", "who"]):
            context_parts.append("## OneFlow Users (Mocked)")
            context_parts.append("- User: Developer (active)")
            context_parts.append("- User: Business Analyst (active)")
        
        if not context_parts:
            # No relevant context found
            logging.debug(f"[ONEFLOW_SOURCE] No relevant OneFlow context for query: {search_query[:50]}...")
            return ""
        
        context = "\n".join(context_parts)
        logging.debug(f"[ONEFLOW_SOURCE] Retrieved mocked OneFlow context ({len(context)} characters)")
        return context
    
    def get_source_name(self) -> str:
        """Get the name of this context source."""
        return self._source_name
    
    def is_available(self) -> bool:
        """
        Check if OneFlow context source is available.
        
        Currently always returns True (using mocked data).
        When API integration is implemented, this will check API connectivity.
        
        Returns:
            bool: True if source is available, False otherwise
        """
        # TODO: When API is implemented, check connectivity:
        # try:
        #     response = await self._check_api_health()
        #     return response.status_code == 200
        # except:
        #     return False
        
        return True  # Always available when using mocked data
