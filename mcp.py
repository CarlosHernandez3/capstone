# mcp.py

from dotenv import load_dotenv
import os
import logging
from fastmcp import FastMCP

load_dotenv()

try:
    mcp = FastMCP(name="Loan-Agent-MCP")
except Exception as e:
    logging.exception("Mcp initialization Error")
    exit(1)

@mcp.tool("verify_paystub")
def verify_paystub(paystub: object):
    try:
        # Implement paystub verification logic here
        return {"status": "Paystub verified successfully"}
    
    except Exception as e:
        logging.exception("Error in verify_paystub")
        return {"error": f"Exception in verify_paystub: {e}"}

@mcp.tool("verify_id")
def verify_id(id: object):
    try:
        # Implement ID verification logic here
        return {"status": "ID verified successfully"}
    except Exception as e:
        logging.exception("Error in calling verify_id api")
        return {"error": f"Exception in verify_id api call: {e}"}


if __name__ == "__main__":
    logging.info("Validation-MCP starting up...")
    try:
        mcp.run(transport="stdio", host="localhost", port=8001)
    except Exception as e:
        logging.exception("Fatal error in main MCP run")
        exit(1)
