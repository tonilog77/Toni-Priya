def is_gemini_quota_error(exc: Exception) -> bool:
    """
    Check whether the Gemini error is a quota/rate-limit error.
    """

    error_text = str(exc).upper()

    quota_keywords = [
        "GEMINI_QUOTA_EXCEEDED",
        "RESOURCE_EXHAUSTED",
        "QUOTA EXCEEDED",
        "RATE LIMIT",
        "429",
        "GENERATE_CONTENT_FREE_TIER_REQUESTS",
    ]

    return any(
        keyword in error_text
        for keyword in quota_keywords
    )


def get_gemini_error_message(exc: Exception) -> str:
    """
    Convert Gemini API errors into a user-friendly message.
    """

    error_text = str(exc).upper()

    # 429 / quota
    if is_gemini_quota_error(exc):
        return (
            "Gemini API usage limit has been reached. "
            "Please wait until your Gemini quota resets "
            "and then try again."
        )

    # API key / authentication
    if (
        "GEMINI_AUTH_ERROR" in error_text
        or "API KEY" in error_text
        or "UNAUTHENTICATED" in error_text
    ):
        return (
            "Gemini API authentication failed. "
            "Please check your GEMINI_API_KEY in the .env file."
        )

    # Model not found
    if (
        "GEMINI_MODEL_NOT_FOUND" in error_text
        or "NOT_FOUND" in error_text
    ):
        return (
            "The configured Gemini model is not available. "
            "Please check GEMINI_MODEL in your configuration."
        )

    # Permission
    if "PERMISSION_DENIED" in error_text:
        return (
            "Gemini API access was denied. "
            "Please check your Google AI project and API key permissions."
        )

    # Generic error
    return (
        "Gemini could not generate the comic right now. "
        "Please try again."
    )