import os
import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import redis.asyncio as aioredis

from app.db.base import get_db
from app.db.models import AgentRun, AgentOutputChunk

router = APIRouter(prefix="/api", tags=["stream"])


async def create_redis_client():
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    return await aioredis.from_url(redis_url)


@router.get("/runs/{run_id}/stream")
async def stream_run_output(run_id: str, db: Session = Depends(get_db)):
    """
    Stream real-time output from an agent run via SSE.

    Events:
    - stdout: Output line from agent
    - status: Status change (running, success, failed, etc.)
    - history: Buffered output from before connection
    - done: Stream complete
    """
    # Validate run exists
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(404, f"Run {run_id} not found")

    async def event_generator():
        redis = None
        pubsub = None
        channel = f"agent_run:{run_id}:output"

        try:
            # 1. Send any buffered history first
            chunks = db.query(AgentOutputChunk).filter(
                AgentOutputChunk.run_id == run_id
            ).order_by(AgentOutputChunk.chunk_index).all()

            for chunk in chunks:
                lines = chunk.content.split("\n") if chunk.content else []
                for line in lines:
                    event = json.dumps({"type": "history", "content": line})
                    yield f"data: {event}\n\n"

            # 2. If already completed, send final status and done
            if run.status in ["success", "failed", "timeout", "cancelled"]:
                event = json.dumps({
                    "type": "status",
                    "status": run.status,
                    "exit_code": run.exit_code,
                    "result_ref": run.result_ref,
                    "error": run.error_message
                })
                yield f"data: {event}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                return

            # 3. Subscribe to live updates
            try:
                redis = await create_redis_client()
                pubsub = redis.pubsub()
                await pubsub.subscribe(channel)
            except Exception as e:
                # If Redis connection fails, fallback or end
                yield f"data: {json.dumps({'type': 'error', 'message': f'Redis error: {e}'})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                return

            while True:
                try:
                    message = await asyncio.wait_for(
                        pubsub.get_message(ignore_subscribe_messages=True),
                        timeout=30.0  # Heartbeat every 30s
                    )
                except asyncio.TimeoutError:
                    # Send heartbeat
                    yield f": heartbeat\n\n"
                    continue

                if message is None:
                    continue

                raw_data = message["data"]
                if isinstance(raw_data, bytes):
                    raw_data = raw_data.decode("utf-8")

                data = json.loads(raw_data)
                yield f"data: {json.dumps(data)}\n\n"

                # Check for completion
                if data.get("type") == "status" and data.get("status") in [
                    "success", "failed", "timeout", "cancelled"
                ]:
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    break

        except asyncio.TimeoutError:
            # Reconnect hint
            yield f"data: {json.dumps({'type': 'timeout', 'message': 'Reconnect'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            if pubsub:
                try:
                    await pubsub.unsubscribe(channel)
                except Exception:
                    pass
            if redis:
                try:
                    await redis.close()
                except Exception:
                    pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get("/runs/{run_id}/output")
def get_run_output(run_id: str, db: Session = Depends(get_db)):
    """Get full output history (for completed runs)."""
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(404, f"Run {run_id} not found")

    chunks = db.query(AgentOutputChunk).filter(
        AgentOutputChunk.run_id == run_id
    ).order_by(AgentOutputChunk.chunk_index).all()

    output = "\n".join(chunk.content for chunk in chunks if chunk.content)

    return {
        "run_id": run_id,
        "status": run.status,
        "output": output,
        "line_count": run.output_lines,
        "byte_count": run.output_bytes
    }
