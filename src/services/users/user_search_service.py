"""Advanced user search service."""
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.users.user_search_repository import UserSearchRepository
from src.models.auth.user import User


class UserSearchService:
    """Service for advanced user search operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize search service with database session."""
        self.search_repo = UserSearchRepository(session)
        self.session = session
    
    async def search(
        self,
        query: str = "",
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = 'created_at',
        sort_desc: bool = True
    ) -> Dict[str, Any]:
        """
        Perform a search with query string and filters.
        
        Args:
            query: Search query string
            filters: Dictionary of filters (status, dates, fields)
            page: Page number (1-indexed)
            page_size: Number of results per page
            sort_by: Field to sort by
            sort_desc: Sort descending if True
        
        Returns:
            Dictionary with results, pagination, and facets
        """
        filters = filters or {}
        
        # Calculate offset
        skip = (page - 1) * page_size
        
        # Parse filters
        search_params = {
            'search_term': query if query else None,
            'skip': skip,
            'limit': page_size,
            'order_by': sort_by,
            'order_desc': sort_desc
        }
        
        # Status filters
        if 'status' in filters:
            if filters['status'] == 'deleted':
                search_params['only_deleted'] = True
            elif filters['status'] == 'all':
                search_params['include_deleted'] = True
            # default is active only (include_deleted=False)
        
        # Field-specific filters
        if 'first_name' in filters:
            search_params['first_name'] = filters['first_name']
        if 'last_name' in filters:
            search_params['last_name'] = filters['last_name']
        if 'email' in filters:
            search_params['email'] = filters['email']
        
        # Date range filters
        if 'created_after' in filters:
            search_params['created_after'] = self._parse_date(filters['created_after'])
        if 'created_before' in filters:
            search_params['created_before'] = self._parse_date(filters['created_before'])
        if 'updated_after' in filters:
            search_params['updated_after'] = self._parse_date(filters['updated_after'])
        if 'updated_before' in filters:
            search_params['updated_before'] = self._parse_date(filters['updated_before'])
        
        # Perform search
        result = await self.search_repo.advanced_search(**search_params)
        
        # Format response
        return {
            'users': [self._format_user(user) for user in result['users']],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': result['total'],
                'pages': result['pages'],
                'has_next': page < result['pages'],
                'has_prev': page > 1
            },
            'facets': result['facets'],
            'query': query,
            'filters': filters
        }
    
    async def quick_search(
        self,
        query: str,
        limit: int = 10,
        include_deleted: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Quick search for autocomplete/typeahead.
        Returns simplified user data.
        """
        result = await self.search_repo.advanced_search(
            search_term=query,
            limit=limit,
            include_deleted=include_deleted
        )
        
        return [
            {
                'id': user.id,
                'name': f"{user.first_name} {user.last_name}",
                'email': user.email,
                'is_deleted': user.is_deleted
            }
            for user in result['users']
        ]
    
    async def get_suggestions(
        self,
        partial_term: str,
        field: str = 'all',
        limit: int = 5
    ) -> List[str]:
        """Get autocomplete suggestions."""
        return await self.search_repo.search_suggestions(
            partial_term=partial_term,
            field=field,
            limit=limit
        )
    
    async def search_by_date_range(
        self,
        date_field: str = 'created_at',
        days_ago: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[User]:
        """
        Search users by date range.
        
        Args:
            date_field: 'created_at' or 'updated_at'
            days_ago: Number of days to look back from today
            start_date: Start date for range
            end_date: End date for range
        """
        search_params = {}
        
        if days_ago:
            start_date = datetime.now().date() - timedelta(days=days_ago)
            end_date = datetime.now().date()
        
        if date_field == 'created_at':
            if start_date:
                search_params['created_after'] = start_date
            if end_date:
                search_params['created_before'] = end_date
        elif date_field == 'updated_at':
            if start_date:
                search_params['updated_after'] = start_date
            if end_date:
                search_params['updated_before'] = end_date
        
        result = await self.search_repo.advanced_search(**search_params)
        return result['users']
    
    async def find_duplicates(
        self,
        field: str = 'email'
    ) -> Dict[str, List[User]]:
        """
        Find duplicate users by a specific field.
        
        Returns a dictionary where keys are duplicate values
        and values are lists of users with that value.
        """
        from sqlalchemy import select, func
        
        # Find duplicate values
        subquery = (
            select(
                getattr(User, field),
                func.count(User.id).label('count')
            )
            .where(User.is_deleted == False)
            .group_by(getattr(User, field))
            .having(func.count(User.id) > 1)
            .subquery()
        )
        
        # Get users with duplicate values
        query = (
            select(User)
            .where(
                getattr(User, field).in_(
                    select(subquery.c[field])
                ),
                User.is_deleted == False
            )
            .order_by(getattr(User, field))
        )
        
        result = await self.session.execute(query)
        users = result.scalars().all()
        
        # Group by duplicate value
        duplicates = {}
        for user in users:
            value = getattr(user, field)
            if value not in duplicates:
                duplicates[value] = []
            duplicates[value].append(user)
        
        return duplicates
    
    async def export_search_results(
        self,
        search_params: Dict[str, Any],
        format: str = 'csv'
    ) -> str:
        """
        Export search results to CSV or JSON format.
        
        Args:
            search_params: Same parameters as search()
            format: 'csv' or 'json'
        
        Returns:
            Formatted string with the data
        """
        # Get all results without pagination
        search_params['skip'] = 0
        search_params['limit'] = 10000  # Set a reasonable max
        
        result = await self.search_repo.advanced_search(**search_params)
        
        if format == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=['id', 'first_name', 'last_name', 'email', 'created_at', 'updated_at', 'is_deleted']
            )
            writer.writeheader()
            
            for user in result['users']:
                writer.writerow({
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'created_at': user.created_at.isoformat(),
                    'updated_at': user.updated_at.isoformat() if user.updated_at else '',
                    'is_deleted': user.is_deleted
                })
            
            return output.getvalue()
        
        elif format == 'json':
            import json
            
            data = [
                {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'created_at': user.created_at.isoformat(),
                    'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                    'is_deleted': user.is_deleted
                }
                for user in result['users']
            ]
            
            return json.dumps(data, indent=2)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def get_search_stats(self) -> Dict[str, Any]:
        """Get statistics about users for search context."""
        result = await self.search_repo.advanced_search(limit=0)
        facets = result['facets']
        
        # Calculate additional stats
        total_users = facets['status']['active'] + facets['status']['deleted']
        
        stats = {
            'total_users': total_users,
            'active_users': facets['status']['active'],
            'deleted_users': facets['status']['deleted'],
            'deletion_rate': (
                facets['status']['deleted'] / total_users * 100
                if total_users > 0 else 0
            ),
            'date_range': facets.get('dates', {})
        }
        
        # Get recent activity
        recent_created = await self.search_by_date_range(
            date_field='created_at',
            days_ago=7
        )
        recent_updated = await self.search_by_date_range(
            date_field='updated_at',
            days_ago=7
        )
        
        stats['recent_activity'] = {
            'created_last_week': len(recent_created),
            'updated_last_week': len(recent_updated)
        }
        
        return stats
    
    def _format_user(self, user: User) -> Dict[str, Any]:
        """Format user object for response."""
        return {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
            'deleted_at': user.deleted_at.isoformat() if user.deleted_at else None,
            'is_deleted': user.is_deleted,
            'status': 'deleted' if user.is_deleted else 'active'
        }
    
    def _parse_date(self, date_str: Any) -> date:
        """Parse date from various formats."""
        if isinstance(date_str, date):
            return date_str
        if isinstance(date_str, datetime):
            return date_str.date()
        if isinstance(date_str, str):
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            # Try ISO format
            try:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
            except:
                pass
        raise ValueError(f"Cannot parse date: {date_str}")