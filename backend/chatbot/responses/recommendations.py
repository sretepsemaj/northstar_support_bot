from backend.services.recommendation_service import RecommendationResult


def format_recommendation_response(result: RecommendationResult) -> str:
    if result.needs_clarification:
        questions = "\n".join(f"- {question}" for question in result.questions)
        return f"{result.message}\n\n{questions}"

    return result.message
