def nav(request):
    return {
        "nav_items": [
            ("dashboard", "Dashboard"),
            ("predictor", "Predictor"),
            ("results", "Results"),
            ("analytics", "Analytics"),
            ("history", "History"),
        ],
        "active_page": getattr(request, "active_page", ""),
    }