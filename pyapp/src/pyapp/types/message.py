
from datetime import datetime
from enum import Enum
import uuid
from pydantic import BaseModel
from typing import List, Optional, Any

class ClientAttachment(BaseModel):
    name: str
    contentType: str
    url: str


class ToolInvocationState(str, Enum):
    CALL = 'call'
    PARTIAL_CALL = 'partial-call'
    RESULT = 'result'

class ToolInvocation(BaseModel):
    state: ToolInvocationState
    toolCallId: str
    toolName: str
    args: Any
    result: Any

class UIMessage(BaseModel):
    id: Optional[uuid.UUID | str] = None
    content: str
    createdAt: Optional[str | datetime] = None
    role: str

class ClientMessage(BaseModel):
    role: str
    content: str
    experimental_attachments: Any = None
    toolInvocations: Any = None

    class Config:
        extra = "ignore" 
