from fastapi import APIRouter, HTTPException, Depends, FastAPI, Request
from pydantic import BaseModel, ValidationError
from typing import Optional
import logging
from tfo_chatbot import TFOChatbot
from tfo_llm_chatbot import GenAIChatbot
from contextlib import AsyncExitStack
import traceback
import time
import json

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])
chatbot = TFOChatbot()
llmChatbot = GenAIChatbot()
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


class ChatQuery(BaseModel):
    user_role: str
    query: str
    employee_id: Optional[str] = None

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

@router.post("/tfo-bot")
async def tfo_bot(request: Request):
    """Handle employee queries for finding positions via LLM-backed chatbot."""
    try:
        body = await request.json()
    except Exception:
        # try form data
        try:
            form = await request.form()
            body = dict(form)
        except Exception:
            # try raw bytes -> text -> json
            try:
                raw = await request.body()
                if raw:
                    body = json.loads(raw.decode("utf-8"))
                else:
                    # fallback to query params
                    body = dict(request.query_params)
            except Exception:
                body = dict(request.query_params)

    try:
        payload = EmployeeQuery.parse_obj(body)
    except ValidationError as e:
        # return pydantic validation details instead of a generic 422
        raise HTTPException(status_code=422, detail=json.loads(e.json()))

    try:
        response = await llmChatbot.process_chat_llm(payload.employee_id, payload.query)
        return {
            "status": "success",
            "employee_id": payload.employee_id,
            "query": payload.query,
            "response": response
        }
    except Exception as e:
        logger.error(f"Error processing employee query: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process query")

@router.post("/chat")
async def handle_chat_query(request: Request):
    """Unified endpoint for all chat queries using GenAI.

    Accepts JSON body: {"user_role":..., "query":..., "employee_id": optional}
    """
    try:
        body = await request.json()
    except Exception:
        # try form data
        try:
            form = await request.form()
            body = dict(form)
        except Exception:
            # try raw bytes -> text -> json
            try:
                raw = await request.body()
                if raw:
                    body = json.loads(raw.decode("utf-8"))
                else:
                    # fallback to query params
                    body = dict(request.query_params)
            except Exception:
                body = dict(request.query_params)

    print('data parsed')
    logger.info("/chat parsed body: %s", body)

    try:
        payload = ChatQuery.parse_obj(body)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=json.loads(e.json()))

    # delegate to helper to keep logic reusable
    return await _process_chat_payload(payload)


async def _process_chat_payload(payload: ChatQuery):
    try:
        print('before the chat call')
        response = await llmChatbot.process_query(
            user_role=payload.user_role,
            query=payload.query,
            employee_id=payload.employee_id,
        )
        print('after the chat call')
        return {
            "status": "success",
            "user_role": payload.user_role,
            "query": payload.query,
            "response": response,
        }
    except Exception as e:
        logger.error(f"Error processing chat query: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process query")

# Keep legacy endpoints for backward compatibility
@router.post("/employee/query")
async def handle_employee_query_legacy(request: ChatQuery):
    """Legacy employee endpoint"""
    return await _process_chat_payload(request)


@router.post("/manager/query")
async def handle_manager_query_legacy(request: ChatQuery):
    """Legacy manager endpoint"""
    return await _process_chat_payload(request)


# include router into app
app.include_router(router)
