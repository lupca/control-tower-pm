from typing import Optional, Dict, Any, Union
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

from app.graph.state import TaskState, GateType, Mode, FourEyesViolation
from app.graph.nodes import (
    parse_input_node,
    spec_node,
    plan_node,
    dispatch_node,
    review_order_node,
    verdict_node
)


class CustomControlTowerGraph:
    """Wrapper around StateGraph or graph invocation to support step-by-step gate transitions and state management."""

    def __init__(self, checkpointer: Optional[BaseCheckpointSaver] = None):
        self.checkpointer = checkpointer or MemorySaver()
        builder = StateGraph(TaskState)

        builder.add_node("parse_input", parse_input_node)
        builder.add_node("spec", spec_node)
        builder.add_node("plan", plan_node)
        builder.add_node("dispatch", dispatch_node)
        builder.add_node("review_order", review_order_node)
        builder.add_node("verdict", verdict_node)

        builder.add_edge(START, "parse_input")

        self.compiled_graph = builder.compile(checkpointer=self.checkpointer)
        self.state = TaskState()

    def invoke(self, input_data: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if input_data is None:
            input_data = {}

        # Update local state with input_data
        for k, v in input_data.items():
            if hasattr(self.state, k) and v is not None:
                setattr(self.state, k, v)

        # Handle verdict (highest priority when verdict key passed)
        if input_data.get("verdict") is not None:
            if input_data.get("reviewer"):
                self.state.reviewer = input_data["reviewer"]
            res = verdict_node(self.state)
            for k, v in res.items():
                setattr(self.state, k, v)
            return self.state.model_dump()

        raw = self.state.raw_input.strip()

        # Handle explicit /review-order command passed in this invocation
        if input_data.get("raw_input") and input_data["raw_input"].strip().startswith("/review-order"):
            res = review_order_node(self.state)
            for k, v in res.items():
                setattr(self.state, k, v)
            return self.state.model_dump()

        # Mode: bypass
        if self.state.mode == Mode.BYPASS:
            res_spec = spec_node(self.state)
            for k, v in res_spec.items():
                setattr(self.state, k, v)

            res_plan = plan_node(self.state)
            for k, v in res_plan.items():
                setattr(self.state, k, v)

            res_disp = dispatch_node(self.state)
            for k, v in res_disp.items():
                setattr(self.state, k, v)

            return self.state.model_dump()

        # Mode: supervised or default flow
        # 1. Spec Gate
        if self.state.current_gate == GateType.SPEC and self.state.approval != "approve":
            res = spec_node(self.state)
            for k, v in res.items():
                setattr(self.state, k, v)
            return self.state.model_dump()

        # 2. Transition from spec -> plan if approved
        if self.state.current_gate == GateType.SPEC and self.state.approval == "approve":
            self.state.approval = None  # reset approval for plan gate
            res = plan_node(self.state)
            for k, v in res.items():
                setattr(self.state, k, v)
            return self.state.model_dump()

        # 3. Transition from plan -> dispatch if approved
        if self.state.current_gate == GateType.PLAN and self.state.approval == "approve":
            self.state.approval = None
            res = dispatch_node(self.state)
            for k, v in res.items():
                setattr(self.state, k, v)
            return self.state.model_dump()

        # 4. Dispatch gate execution if already at dispatch
        if self.state.current_gate == GateType.DISPATCH:
            res = dispatch_node(self.state)
            for k, v in res.items():
                setattr(self.state, k, v)
            return self.state.model_dump()

        return self.state.model_dump()


def build_graph(checkpointer: Optional[BaseCheckpointSaver] = None):
    return CustomControlTowerGraph(checkpointer=checkpointer)
