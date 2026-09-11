# Model Context Protocol server
"""
Model Context Protocol (MCP) Server Implementation
Provides a standardized interface for LLM interactions with tools
"""
from typing import Dict, Any, List, Optional
from utils.logger import log
import json


class MCPServer:
    """MCP Server for standardized tool communication"""
    
    def __init__(self):
        self.tools = {}
        self.context = {}
        log.info("MCP Server initialized")
    
    def register_tool(self, tool_name: str, tool_instance: Any):
        """Register a tool with the MCP server
        
        Args:
            tool_name: Name of the tool
            tool_instance: Tool instance
        """
        self.tools[tool_name] = tool_instance
        log.info(f"MCP: Registered tool '{tool_name}'")
    
    def call_tool(
        self,
        tool_name: str,
        action: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call a registered tool through MCP
        
        Args:
            tool_name: Name of the tool
            action: Action to perform
            parameters: Action parameters
            
        Returns:
            Tool execution result
        """
        try:
            if tool_name not in self.tools:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not registered"
                }
            
            tool = self.tools[tool_name]
            
            # Update context
            self.context["last_tool"] = tool_name
            self.context["last_action"] = action
            
            # Execute tool
            log.info(f"MCP: Calling {tool_name}.{action}")
            result = tool._run(action=action, **parameters)
            
            # Store result in context
            self.context["last_result"] = result
            
            return result
            
        except Exception as e:
            log.error(f"MCP tool call error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_context(self) -> Dict[str, Any]:
        """Get current MCP context
        
        Returns:
            Current context
        """
        return self.context.copy()
    
    def update_context(self, key: str, value: Any):
        """Update MCP context
        
        Args:
            key: Context key
            value: Context value
        """
        self.context[key] = value
        log.debug(f"MCP: Context updated - {key}")
    
    def clear_context(self):
        """Clear MCP context"""
        self.context = {}
        log.info("MCP: Context cleared")
    
    def list_tools(self) -> List[str]:
        """List all registered tools
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a tool
        
        Args:
            tool_name: Tool name
            
        Returns:
            Tool information
        """
        if tool_name not in self.tools:
            return None
        
        tool = self.tools[tool_name]
        return {
            "name": tool.name,
            "description": tool.description,
            "registered": True
        }
    
    def execute_workflow(self, workflow_steps: List[Dict]) -> List[Dict]:
        """Execute a workflow of multiple tool calls
        
        Args:
            workflow_steps: List of workflow steps with tool calls
            
        Returns:
            List of results for each step
        """
        results = []
        
        for step in workflow_steps:
            tool_name = step.get("tool")
            action = step.get("action")
            parameters = step.get("parameters", {})
            
            result = self.call_tool(tool_name, action, parameters)
            results.append({
                "step": step.get("name", "unnamed"),
                "tool": tool_name,
                "action": action,
                "result": result
            })
            
            # Stop on error if specified
            if not result.get("success") and step.get("stop_on_error", False):
                log.warning(f"Workflow stopped at step '{step.get('name')}' due to error")
                break
        
        return results


# Global MCP server instance
mcp_server = MCPServer()


# Initialize and register all tools
def initialize_mcp_server():
    """Initialize MCP server with all tools"""
    from tools.resume_parser_tool import resume_parser_tool
    from tools.database_tool import database_tool
    from tools.vector_search_tool import vector_search_tool
    from tools.email_tool import email_tool
    from tools.calendar_tool import calendar_tool
    
    # Register all tools
    mcp_server.register_tool("resume_parser", resume_parser_tool)
    mcp_server.register_tool("database", database_tool)
    mcp_server.register_tool("vector_search", vector_search_tool)
    mcp_server.register_tool("email", email_tool)
    mcp_server.register_tool("calendar", calendar_tool)
    
    log.info("MCP Server fully initialized with all tools")