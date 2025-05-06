from pydantic import BaseModel
from enum import Enum
from typing import List
import json

class ToolCallType(Enum):
    REFERENCES = "references"

class ToolCallResultType(BaseModel):
    type: ToolCallType

    def dict(self):
        return {"type":self.type.value}
    
class Reference(BaseModel):
    id: int | str
    content: str

class ToolCall(BaseModel):
    toolCallId: str
    toolName: str
    args: ToolCallResultType

class ToolCallResult(BaseModel):
    result: List[Reference]

    def list_dict(self):
        return [r.model_dump() for r in self.result]

class VercelStream:
    @staticmethod
    def stream_text(text:str):
        return f'0:{json.dumps(text)}\n',text

    @staticmethod
    def stream_tool_call(tool_call:ToolCall , results:ToolCallResult):
        initial = dict(toolCallId=tool_call.toolCallId,toolName=tool_call.toolName)
        yield f'b:{json.dumps(initial)}\n',None
        delta_phase = dict(toolCallId=tool_call.toolCallId,argsTextDelta="")
        yield f'c:{json.dumps(delta_phase)}\n',None
        args = dict(toolCallId=tool_call.toolCallId,toolName=tool_call.toolName,args=tool_call.args.dict())
        yield f'9:{json.dumps(args)}\n',None
        final = dict(toolCallId=tool_call.toolCallId,result=results.list_dict())
        yield f'a:{json.dumps(final)}\n',final
        
    
    @staticmethod
    def stream_finish(promptTokens:int,completionTokens:int):
        final = dict(finishReason="stop",usage=dict(promptTokens=promptTokens,completionTokens=completionTokens))
        return f'd:{json.dumps(final)}\n',final
    