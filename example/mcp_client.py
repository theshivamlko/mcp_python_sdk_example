

from mcp.client.stdio import stdio_client
from mcp import ClientSession,StdioServerParameters,types
from pydantic import AnyUrl
from mcp.client.streamable_http import streamablehttp_client


server_params = StdioServerParameters(command="uv",
                                      args=["run","mcp", "run", "server.py:notes_mcp"])

async def run():
    # async with stdio_client(server_params) as (read,write):
    async with streamablehttp_client(url="http://127.0.0.1:7000/mcp") as (read,write,_):
        async with ClientSession(read,write) as sessions:
            
            await sessions.initialize()
            
            prompts=await sessions.list_prompts()
            print("Available Prompts:", prompts.prompts[0].name)
            
            tools=await sessions.list_tools()
            print("Available Tools:", tools)
            
            resources=await sessions.list_resources()
            print("Available Resources:", resources.resources[0].uri)
            
            if prompts.prompts:
                
                prompts=await sessions.get_prompt(prompts.prompts[0].name,arguments={"name":"Test Note Prompt"})
                print("Prompt Details:", prompts.messages[0].content)
            
            resources=await sessions.read_resource(AnyUrl(resources.resources[0].uri))
            content_block=resources.contents[0]
            
            if isinstance(content_block,types.TextContent):
                print("Resource Content:", content_block.text)
                
            
            result=None
            response=None
            for tool in tools.tools:
                if tool.name=="add_note":
                    response=await sessions.call_tool(name=tool.name,arguments={"name":"Test Note","content":"This is a test note."})
                    result= response.content[0]
                    print("Add Note Response:", response)
                elif tool.name=="list_notes":
                    response=await sessions.call_tool(name=tool.name,arguments={})
                    result= response.content[0]
                    print("List Notes Response:", response)
                elif tool.name=="get_note":
                    response=await sessions.call_tool(name=tool.name,arguments={})
                    result= response.content[0]
                    print("Get Note Response:", response)
                elif tool.name=="delete_note":
                    response=await sessions.call_tool(name=tool.name,arguments={})
                    result= response.content[0]
                    print("Delete Note Response:", response)

            if isinstance(result, types.TextContent):
                print("Final Result:", result.text)
            
            result_formatted=response.structuredContent
            print("Final Result (formatted):", result_formatted)
                
            
            
            
def main():
    import asyncio
    asyncio.run(run())       

if __name__ == "__main__":
     main()