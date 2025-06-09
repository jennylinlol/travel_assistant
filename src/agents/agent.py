import datetime
import operator
import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from agents.tools.flights_finder import flights_finder
from agents.tools.hotels_finder import hotels_finder
from agents.tools.weather_check import weather_check

_ = load_dotenv()

CURRENT_YEAR = datetime.datetime.now().year


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


TOOLS_SYSTEM_PROMPT = f"""You are a smart travel agency. Use the tools to look up information.
    You are allowed to make multiple calls (either together or in sequence).
    Only look up information when you are sure of what you want.
    The current year is {CURRENT_YEAR}.
    If you need to look up some information before asking a follow up question, you are allowed to do that!
    I want to have in your output links to hotels websites and flights websites (if possible).
    I want to have as well the logo of the hotel. (if possible).
    In your output always include the price of the flight and the price of the hotel and the currency as well (if possible).
    for example for hotels-
    Rate: $581 per night
    Total: $3,488
    """

TOOLS = [flights_finder, hotels_finder, weather_check]


class AgentError(Exception):
    """Base exception for agent errors"""
    pass

class ToolExecutionError(AgentError):
    """Exception for tool execution errors"""
    pass


class Agent:
    def __init__(self):
        self._tools = {t.name: t for t in TOOLS}
        self._tools_llm = ChatOpenAI(
            model_name=os.environ.get('OPENAI_MODEL', 'gpt-4o'),
            api_key=os.environ.get('OPENAI_API_KEY'),
        ).bind_tools(TOOLS)

        builder = StateGraph(AgentState)
        builder.add_node('call_tools_llm', self.call_tools_llm)
        builder.add_node('invoke_tools', self.invoke_tools)
        builder.set_entry_point('call_tools_llm')

        builder.add_conditional_edges('call_tools_llm', Agent.exists_action, {'more_tools': 'invoke_tools', 'done': END})
        builder.add_edge('invoke_tools', 'call_tools_llm')
        memory = MemorySaver()
        self.graph = builder.compile(checkpointer=memory)

        self._error_count = 0
        self._max_retries = 3

    @staticmethod
    def exists_action(state: AgentState):
        result = state['messages'][-1]
        if hasattr(result, 'tool_calls') and len(result.tool_calls) > 0:
            return 'more_tools'
        return 'done'

    def call_tools_llm(self, state: AgentState):
        messages = state['messages']
        messages = [SystemMessage(content=TOOLS_SYSTEM_PROMPT)] + messages
        message = self._tools_llm.invoke(messages)
        return {'messages': [message]}

    def invoke_tools(self, state: AgentState):
        tool_calls = state['messages'][-1].tool_calls
        results = []
        failed_tools = []
        
        # Process each tool call
        for tool_call in tool_calls:
            tool_name = tool_call['name']
            tool_id = tool_call['id']
            
            try:
                if tool_name not in self._tools:
                    raise ToolExecutionError(f"Tool '{tool_name}' not found")
                
                result = self._tools[tool_name].invoke(tool_call['args'])
                
                # Handle error responses from tools
                if isinstance(result, dict) and 'error' in result:
                    failed_tools.append(tool_name)
                    error_msg = self._format_error_message(tool_name, result['error'])
                    result = error_msg
                
                results.append(ToolMessage(tool_call_id=tool_id, name=tool_name, content=str(result)))
                
            except Exception as e:
                failed_tools.append(tool_name)
                error_msg = self._format_error_message(tool_name, str(e))
                results.append(ToolMessage(tool_call_id=tool_id, name=tool_name, content=error_msg))

        # If we have failed tools, increment error count
        if failed_tools:
            self._error_count += 1
        
        # If we've exceeded max retries, force completion
        if self._error_count >= self._max_retries:
            final_message = self._generate_fallback_plan(state['messages'][0].content, failed_tools)
            return {'messages': [final_message]}
        
        return {'messages': results}

    def _format_error_message(self, tool_name: str, error: str) -> str:
        """Format error messages consistently"""
        return f"[{tool_name.upper()} ERROR] {error}. The assistant will continue with available information."

    def _generate_fallback_plan(self, original_prompt: str, failed_tools: list) -> AnyMessage:
        """Generate a fallback plan when tools fail"""
        fallback_prompt = f"""
        The following tools failed: {', '.join(failed_tools)}.
        Original request: {original_prompt}
        
        Please generate a travel plan using only the information we have available.
        Focus on providing:
        1. A general daily itinerary
        2. Local attractions and restaurant recommendations
        3. General packing tips
        4. A basic travel checklist
        
        Clearly indicate which information is missing and provide alternative suggestions where possible.
        """
        
        messages = [
            SystemMessage(content=TOOLS_SYSTEM_PROMPT),
            HumanMessage(content=fallback_prompt)
        ]
        
        return self._tools_llm.invoke(messages)