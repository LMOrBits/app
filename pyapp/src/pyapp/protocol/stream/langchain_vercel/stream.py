
from pyapp.types.message import ClientMessage
from pyapp.protocol.stream.vercel.protocol import VercelStream,ToolCall,ToolCallResult,ToolCallType,Reference,ToolCallResultType
from pyapp.log.log_config import get_logger
from pyapp.types import ClientMessage 
from typing import List

logger = get_logger()

  
async def stream_tool_call(messages: List[ClientMessage],chain, protocol: str = 'data'):  
  async for event in chain.astream_events(messages[-1].content, version="v2",include_names=["Docs","stream"]):
      kind = event["event"]
      if kind == "on_chat_model_stream":
          yield VercelStream.stream_text(event['data']['chunk'].content)
      if kind == "on_retriever_end":
        docs = []
        for i,doc in enumerate(event['data']['output']):
          if "markdown" in doc.metadata:
            docs.append(Reference(id=i,content=doc.metadata["markdown"]))
          else:
            docs.append(Reference(id=i,content=doc.page_content))
        tool_call = ToolCall(toolCallId=event['run_id'],toolName="streaming-tool",args=ToolCallResultType(type=ToolCallType.REFERENCES))
        tool_result = ToolCallResult(result=docs)
        for t in VercelStream.stream_tool_call(tool_call,tool_result):
            yield t
          
  yield VercelStream.stream_finish(10,20)
    

