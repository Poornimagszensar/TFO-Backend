from fastapi import APIRouter, HTTPException, Depends, FastAPI, Request
from pydantic import BaseModel
from typing import Optional
import logging
from tfo_chatbot import TFOChatbot
from contextlib import AsyncExitStack
import traceback
import time

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])
chatbot = TFOChatbot()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()


# Middleware: ensure AsyncExitStack exists in request.scope early
@app.middleware("http")
async def add_async_exit_stack(request: Request, call_next):
    start = time.time()
    stack = AsyncExitStack()
    try:
        await stack.__aenter__()
        request.scope["fastapi_middleware_astack"] = stack
        logger.info("Injected AsyncExitStack into scope for path=%s", request.url.path)
        response = await call_next(request)
        return response
    except Exception:
        logger.error("Middleware caught exception:\n%s", traceback.format_exc())
        raise
    finally:
        try:
            await stack.__aexit__(None, None, None)
        except Exception:
            logger.exception("Error exiting AsyncExitStack")
        elapsed = time.time() - start
        logger.info("add_async_exit_stack completed in %.3fs", elapsed)


class EmployeeQuery(BaseModel):
    employee_id: str
    query: str


class ManagerQuery(BaseModel):
    user_role: str
    query: str


@router.post("/employee/query")
async def handle_employee_query(request: EmployeeQuery):
    """Handle employee queries for finding positions"""
    try:
        response = await chatbot.process_employee_query(request.employee_id, request.query)
        return {
            "status": "success",
            "employee_id": request.employee_id,
            "query": request.query,
            "response": response
        }
    except Exception as e:
        logger.error(f"Error processing employee query: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process query")

@router.post("/manager/query")
async def handle_manager_query(request: ManagerQuery):
    """Handle manager/TSC queries for finding employees"""
    try:
        response = await chatbot.process_manager_query(request.user_role, request.query)
        return {
            "status": "success",
            "user_role": request.user_role,
            "query": request.query,
            "response": response
        }
    except Exception as e:
        logger.error(f"Error processing manager query: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process query")

@router.get("/employees/{employee_id}/opportunities")
async def get_employee_opportunities(employee_id: str):
    """Get open positions for employee"""
    try:
        response = await chatbot.process_employee_query(
            employee_id, 
            "find open positions matching my skills"
        )
        return response
    except Exception as e:
        logger.error(f"Error getting opportunities: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get opportunities")


@router.get("/health")
async def health(request: Request):
    present = isinstance(request.scope.get("fastapi_middleware_astack"), AsyncExitStack)
    return {"middleware_stack_present": present, "scope_keys": list(request.scope.keys())}


# include router into app
app.include_router(router)
