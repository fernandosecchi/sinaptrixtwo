"""Advanced search repository for users."""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy import select, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.auth.user import User


class UserSearchRepository:
    """Repository for advanced user search operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize search repository with database session."""
        self.session = session
    
    async def advanced_search(
        self,
        # Text search
        search_term: Optional[str] = None,
        search_fields: Optional[List[str]] = None,
        # Specific filters
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        # Date range filters
        created_after: Optional[date] = None,
        created_before: Optional[date] = None,
        updated_after: Optional[date] = None,
        updated_before: Optional[date] = None,
        # Status filters
        include_deleted: bool = False,
        only_deleted: bool = False,
        # Pagination and sorting
        skip: int = 0,
        limit: int = 100,
        order_by: str = 'created_at',
        order_desc: bool = True
    ) -> Dict[str, Any]:
        """
        Perform advanced search with multiple filters.
        
        Returns dict with:
        - users: List of matching users
        - total: Total count of matching users
        - facets: Aggregated data for filters
        """
        # Build base query
        query = select(User)
        count_query = select(func.count(User.id))
        
        # Apply status filters
        if only_deleted:
            query = query.where(User.is_deleted == True)
            count_query = count_query.where(User.is_deleted == True)
        elif not include_deleted:
            query = query.where(User.is_deleted == False)
            count_query = count_query.where(User.is_deleted == False)
        
        # Apply general search term
        if search_term:
            search_term = search_term.strip()
            if search_fields:
                # Search only in specified fields
                conditions = []
                for field in search_fields:
                    if hasattr(User, field):
                        conditions.append(
                            getattr(User, field).ilike(f"%{search_term}%")
                        )
                if conditions:
                    query = query.where(or_(*conditions))
                    count_query = count_query.where(or_(*conditions))
            else:
                # Search in all text fields
                query = query.where(
                    or_(
                        User.first_name.ilike(f"%{search_term}%"),
                        User.last_name.ilike(f"%{search_term}%"),
                        User.email.ilike(f"%{search_term}%"),
                        # Search in full name
                        func.concat(User.first_name, ' ', User.last_name).ilike(f"%{search_term}%")
                    )
                )
                count_query = count_query.where(
                    or_(
                        User.first_name.ilike(f"%{search_term}%"),
                        User.last_name.ilike(f"%{search_term}%"),
                        User.email.ilike(f"%{search_term}%"),
                        func.concat(User.first_name, ' ', User.last_name).ilike(f"%{search_term}%")
                    )
                )
        
        # Apply specific field filters
        if first_name:
            query = query.where(User.first_name.ilike(f"%{first_name}%"))
            count_query = count_query.where(User.first_name.ilike(f"%{first_name}%"))
        
        if last_name:
            query = query.where(User.last_name.ilike(f"%{last_name}%"))
            count_query = count_query.where(User.last_name.ilike(f"%{last_name}%"))
        
        if email:
            query = query.where(User.email.ilike(f"%{email}%"))
            count_query = count_query.where(User.email.ilike(f"%{email}%"))
        
        # Apply date filters
        if created_after:
            query = query.where(User.created_at >= created_after)
            count_query = count_query.where(User.created_at >= created_after)
        
        if created_before:
            query = query.where(User.created_at <= created_before)
            count_query = count_query.where(User.created_at <= created_before)
        
        if updated_after:
            query = query.where(User.updated_at >= updated_after)
            count_query = count_query.where(User.updated_at >= updated_after)
        
        if updated_before:
            query = query.where(User.updated_at <= updated_before)
            count_query = count_query.where(User.updated_at <= updated_before)
        
        # Get total count
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply ordering
        order_column = getattr(User, order_by, User.created_at)
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await self.session.execute(query)
        users = list(result.scalars().all())
        
        # Get facets for filtering
        facets = await self._get_facets(include_deleted, only_deleted)
        
        return {
            'users': users,
            'total': total,
            'facets': facets,
            'page': skip // limit + 1,
            'pages': (total + limit - 1) // limit
        }
    
    async def _get_facets(self, include_deleted: bool = False, only_deleted: bool = False) -> Dict[str, Any]:
        """Get aggregated data for filter facets."""
        facets = {}
        
        # Base condition for status
        if only_deleted:
            base_condition = User.is_deleted == True
        elif not include_deleted:
            base_condition = User.is_deleted == False
        else:
            base_condition = True
        
        # Count by status
        active_count_query = select(func.count(User.id)).where(User.is_deleted == False)
        deleted_count_query = select(func.count(User.id)).where(User.is_deleted == True)
        
        active_result = await self.session.execute(active_count_query)
        deleted_result = await self.session.execute(deleted_count_query)
        
        facets['status'] = {
            'active': active_result.scalar() or 0,
            'deleted': deleted_result.scalar() or 0
        }
        
        # Date ranges
        if base_condition is not True:
            date_query = select(
                func.min(User.created_at).label('min_created'),
                func.max(User.created_at).label('max_created'),
                func.min(User.updated_at).label('min_updated'),
                func.max(User.updated_at).label('max_updated')
            ).where(base_condition)
        else:
            date_query = select(
                func.min(User.created_at).label('min_created'),
                func.max(User.created_at).label('max_created'),
                func.min(User.updated_at).label('min_updated'),
                func.max(User.updated_at).label('max_updated')
            )
        
        date_result = await self.session.execute(date_query)
        date_row = date_result.first()
        
        if date_row:
            facets['dates'] = {
                'min_created': date_row.min_created.isoformat() if date_row.min_created else None,
                'max_created': date_row.max_created.isoformat() if date_row.max_created else None,
                'min_updated': date_row.min_updated.isoformat() if date_row.min_updated else None,
                'max_updated': date_row.max_updated.isoformat() if date_row.max_updated else None
            }
        
        return facets
    
    async def search_with_fuzzy(
        self,
        search_term: str,
        threshold: float = 0.3,
        include_deleted: bool = False,
        limit: int = 10
    ) -> List[User]:
        """
        Search users with fuzzy matching using PostgreSQL's similarity functions.
        Requires pg_trgm extension to be enabled in PostgreSQL.
        """
        # This requires the pg_trgm extension
        # You can enable it with: CREATE EXTENSION IF NOT EXISTS pg_trgm;
        
        query = select(
            User,
            func.similarity(
                func.concat(User.first_name, ' ', User.last_name, ' ', User.email),
                search_term
            ).label('similarity_score')
        )
        
        if not include_deleted:
            query = query.where(User.is_deleted == False)
        
        # Use PostgreSQL's similarity function
        query = query.where(
            func.similarity(
                func.concat(User.first_name, ' ', User.last_name, ' ', User.email),
                search_term
            ) > threshold
        )
        
        query = query.order_by(
            func.similarity(
                func.concat(User.first_name, ' ', User.last_name, ' ', User.email),
                search_term
            ).desc()
        ).limit(limit)
        
        result = await self.session.execute(query)
        return [row[0] for row in result.all()]
    
    async def search_suggestions(
        self,
        partial_term: str,
        field: str = 'all',
        limit: int = 5
    ) -> List[str]:
        """
        Get search suggestions based on partial input.
        Used for autocomplete functionality.
        """
        suggestions = []
        partial_term = partial_term.strip().lower()
        
        if not partial_term:
            return suggestions
        
        if field == 'all' or field == 'first_name':
            query = select(User.first_name).distinct().where(
                User.first_name.ilike(f"{partial_term}%"),
                User.is_deleted == False
            ).limit(limit)
            result = await self.session.execute(query)
            suggestions.extend([row[0] for row in result.all()])
        
        if field == 'all' or field == 'last_name':
            query = select(User.last_name).distinct().where(
                User.last_name.ilike(f"{partial_term}%"),
                User.is_deleted == False
            ).limit(limit)
            result = await self.session.execute(query)
            suggestions.extend([row[0] for row in result.all()])
        
        if field == 'all' or field == 'email':
            query = select(User.email).distinct().where(
                User.email.ilike(f"{partial_term}%"),
                User.is_deleted == False
            ).limit(limit)
            result = await self.session.execute(query)
            suggestions.extend([row[0] for row in result.all()])
        
        # Remove duplicates and limit results
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in seen:
                seen.add(suggestion)
                unique_suggestions.append(suggestion)
                if len(unique_suggestions) >= limit:
                    break
        
        return unique_suggestions
    
    async def bulk_search(
        self,
        search_terms: List[str],
        search_field: str = 'email',
        include_deleted: bool = False
    ) -> Dict[str, Optional[User]]:
        """
        Search for multiple users at once.
        Useful for bulk operations like import validation.
        
        Returns a dict mapping search term to User or None.
        """
        if not search_terms:
            return {}
        
        # Get the field to search
        field = getattr(User, search_field, User.email)
        
        # Build query
        query = select(User).where(field.in_(search_terms))
        
        if not include_deleted:
            query = query.where(User.is_deleted == False)
        
        # Execute query
        result = await self.session.execute(query)
        users = result.scalars().all()
        
        # Map results
        result_map = {}
        for term in search_terms:
            result_map[term] = None
            for user in users:
                if getattr(user, search_field).lower() == term.lower():
                    result_map[term] = user
                    break
        
        return result_map