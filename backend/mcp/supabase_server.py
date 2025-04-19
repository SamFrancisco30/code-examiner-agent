import os
from supabase import create_client, Client
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_connection():
    """Test the connection to Supabase"""
    try:
        # Perform a simple query to check the connection
        response = supabase.table("questions").select("*").execute()
        print(response)
        if response.status_code == 200:
            return "Connection successful!"
        else:
            return f"Connection failed: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# Initialize MCP server
mcp = FastMCP("Supabase Explorer")

@mcp.tool()
def query_data(table_name: str, filter_column: str, filter_value, target_column: str = "*") -> str:
    """
    Query specific data from a table with filtering.
    
    Args:
        table_name (str): The name of the table to query.
        filter_column (str): The column to apply the filter on.
        filter_value: The value to filter by.
        target_column (str): The column(s) to retrieve (default is all columns).
    
    Returns:
        str: The query result or an error message.
    """
    try:
        # Apply the filter and execute the query
        response = supabase.table(table_name).select(target_column).eq(filter_column, filter_value).execute()
        return response.data
    except Exception as e:
        return f"Error executing query: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")