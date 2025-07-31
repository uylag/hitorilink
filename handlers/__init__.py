from .create_handlers import create_router
from .admin_handlers import admin_router
from .interest_handlers import interest_router, build_interests_page
from .search_handlers import search_router
from .edit_handlers import edit_router

__all__ = [
    "create_router", "admin_router", "interest_router",
    "search_router", "edit_router", 
]