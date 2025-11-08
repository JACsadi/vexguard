from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from perplexity import Perplexity
import anyio
import traceback

# --- Initialize Perplexity client ---
client = Perplexity(api_key=os.environ.get("PERPLEXITY_API_KEY"))

router = APIRouter()

# --- Request model ---
class ChatRequest(BaseModel):
    query: str
    age: Optional[int] = None
    context: Optional[str] = None

# --- Response model ---
class ChatResponse(BaseModel):
    success: bool
    response: str
    citations: List[Dict[str, Any]] = []
    relatedQuestions: List[Dict[str, Any]] = []

# --- Helper: normalize lists into dicts ---
def _normalize_to_dict_list(items: Optional[List[Any]]) -> List[Dict[str, Any]]:
    if not items:
        return []
    normalized: List[Dict[str, Any]] = []
    for it in items:
        if isinstance(it, dict):
            normalized.append(it)
        elif isinstance(it, str):
            if it.startswith("http://") or it.startswith("https://"):
                normalized.append({"url": it})
            else:
                normalized.append({"text": it})
        else:
            try:
                normalized.append({"text": str(it)})
            except Exception:
                normalized.append({"text": ""})
    return normalized

# --- Main endpoint ---
@router.post("", response_model=ChatResponse)
async def ai_chat(payload: ChatRequest):
    query = payload.query.strip()
    age = payload.age
    context = payload.context

    if not query:
        raise HTTPException(status_code=400, detail="Missing 'query'")

    # Build system prompt
    system_prompt = (
        "You are a helpful vaccination assistant for Bangladesh.\n\n"
        "Your responsibilities:\n"
        "- Provide accurate vaccine recommendations based on age and health conditions\n"
        "- Explain the Bangladesh EPI (Expanded Programme on Immunization) schedule\n"
        "- Give information about vaccine safety and side effects\n"
        "- Suggest nearby vaccination centers when asked\n"
        "- Provide health awareness and disease prevention tips\n\n"
        "Guidelines:\n"
        "- Always cite official sources (WHO, Bangladesh DGHS, UNICEF)\n"
        "- Use simple, clear language\n"
        "- Prioritize safety and accuracy\n"
        "- For medical emergencies, advise consulting a healthcare provider\n"
        "- please give the response as html property\n"
        "- please give your answer first in bangla then again in english\n"
    )
    if age is not None:
        system_prompt += f"\nUser's age: {age} years"
    if context:
        system_prompt += f"\nConversation context: {context}"

    # --- Call Perplexity in a thread ---
    # --- Call Perplexity in a thread ---
    def call_perplexity():
        return client.chat.completions.create(
            model="sonar-pro",  # keep sonar-pro as requested
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            max_tokens=2000,
            temperature=0.3,
            top_p=0.9,
            search_domain_filter=["dghs.gov.bd", "who.int", "unicef.org", "cdc.gov"],  # added cdc.gov
            return_images=False,
            return_related_questions=True,
            search_recency_filter="month",
            top_k=0,
            stream=False,
            presence_penalty=0,
            frequency_penalty=1,
        )


    try:
        completion = await anyio.to_thread.run_sync(call_perplexity)
    except Exception as e:
        tb = traceback.format_exc()
        print("=== Perplexity call failed ===")
        print(tb)
        return ChatResponse(
            success=False,
            response="Perplexity call failed. See 'error' for details.",
            citations=[],
            relatedQuestions=[]
        )

    # --- Extract response_text safely ---
    response_text = "No response"
    try:
        choice0 = completion.choices[0]
    
    # First try: if 'message' exists with 'content'
        if getattr(choice0, "message", None):
            response_text = getattr(choice0.message, "content", "No response")
    
    # Fallback: if 'text' exists
        elif getattr(choice0, "text", None):
            response_text = choice0.text

    except Exception:
        response_text = "No response"

    # --- Normalize citations & related questions ---
    citations = _normalize_to_dict_list(getattr(completion, "citations", None))
    related_questions = _normalize_to_dict_list(getattr(completion, "related_questions", None))

    return ChatResponse(
        success=True,
        response=response_text,
        citations=citations,
        relatedQuestions=related_questions
    )
