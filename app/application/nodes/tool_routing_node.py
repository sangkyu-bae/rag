from app.infrastructure.graph_state.graph_state import GraphState
from app.infrastructure.route.route_query import RouteQuery


class ToolRoutingNode:
    def __call__(self, state :GraphState)->GraphState:
        question = state["question"]
        # 질문 라우팅
        route: RouteQuery = RouteQuery.get_route_type().invoke({"question": question})
        return route.datasource
