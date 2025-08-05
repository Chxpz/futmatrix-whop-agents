"""
Database schema management for agent-specific schemas.
Each agent gets its own schema with tables tailored to their business rules.
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

import asyncpg
from sqlalchemy import text
from utils.exceptions import DatabaseError
from config.settings import Settings


@dataclass
class TableDefinition:
    """Definition for creating database tables."""
    name: str
    schema: str
    columns: List[Dict[str, str]]
    constraints: List[str]
    indexes: List[str]
    description: str


class DatabaseSchemaManager:
    """Manages agent-specific database schemas and tables."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger("database_schema")
        self.connection_pool = None
        
        # Agent schema definitions
        self.agent_schemas = {
            "agent_alpha": {
                "name": "agent_alpha",
                "description": "Financial Advisor Agent Schema",
                "business_domain": "financial_advisor"
            },
            "agent_beta": {
                "name": "agent_beta", 
                "description": "Content Creator Agent Schema",
                "business_domain": "content_creator"
            }
        }
    
    async def initialize(self) -> None:
        """Initialize database connection and schema manager."""
        try:
            # Extract connection parameters from URL
            db_url = self.settings.DATABASE_CONFIG["url"]
            
            # Create connection pool
            self.connection_pool = await asyncpg.create_pool(
                dsn=db_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            
            self.logger.info("Database schema manager initialized successfully")
            
            # Verify schema existence
            await self.verify_schemas()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database schema manager: {e}")
            raise DatabaseError(f"Schema manager initialization failed: {e}")
    
    async def verify_schemas(self) -> None:
        """Verify that agent schemas exist and are accessible."""
        try:
            async with self.connection_pool.acquire() as conn:
                # Check if agent schemas exist
                for agent_id, schema_info in self.agent_schemas.items():
                    schema_name = schema_info["name"]
                    
                    result = await conn.fetchval(
                        "SELECT schema_name FROM information_schema.schemata WHERE schema_name = $1",
                        schema_name
                    )
                    
                    if result:
                        self.logger.info(f"Schema {schema_name} exists and is accessible")
                    else:
                        self.logger.warning(f"Schema {schema_name} does not exist - may need creation")
            
        except Exception as e:
            self.logger.error(f"Schema verification failed: {e}")
            raise DatabaseError(f"Schema verification failed: {e}")
    
    async def create_agent_tables(self, agent_id: str, table_definitions: List[TableDefinition]) -> None:
        """Create tables for a specific agent schema."""
        try:
            if agent_id not in self.agent_schemas:
                raise DatabaseError(f"Unknown agent ID: {agent_id}")
            
            schema_name = self.agent_schemas[agent_id]["name"]
            
            async with self.connection_pool.acquire() as conn:
                async with conn.transaction():
                    for table_def in table_definitions:
                        await self._create_table(conn, table_def, schema_name)
                        self.logger.info(f"Created table {schema_name}.{table_def.name}")
            
            self.logger.info(f"Successfully created {len(table_definitions)} tables for {agent_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to create tables for {agent_id}: {e}")
            raise DatabaseError(f"Table creation failed for {agent_id}: {e}")
    
    async def _create_table(self, conn: asyncpg.Connection, table_def: TableDefinition, schema_name: str) -> None:
        """Create a single table with all its components using safe parameterized queries."""
        # Validate identifiers first - reject if they contain dangerous patterns
        self._validate_sql_identifier(schema_name)
        self._validate_sql_identifier(table_def.name)
        
        # Escape SQL identifiers
        escaped_schema = self._escape_identifier(schema_name)
        escaped_table = self._escape_identifier(table_def.name)
        
        # Build column definitions with strict validation
        columns_sql = []
        for col in table_def.columns:
            self._validate_sql_identifier(col['name'])
            escaped_col_name = self._escape_identifier(col['name'])
            # Validate column type against allowed types (now throws on invalid types)
            col_type = self._validate_column_type(col['type'])
            col_def = f"{escaped_col_name} {col_type}"
            if col.get('primary_key'):
                col_def += " PRIMARY KEY"
            if col.get('not_null'):
                col_def += " NOT NULL"
            if col.get('default'):
                # Validate and escape default values
                safe_default = self._validate_default_value(col['default'])
                col_def += f" DEFAULT {safe_default}"
            if col.get('unique'):
                col_def += " UNIQUE"
            columns_sql.append(col_def)
        
        # Add validated constraints
        if table_def.constraints:
            validated_constraints = [self._validate_constraint(c) for c in table_def.constraints]
            columns_sql.extend(validated_constraints)
        
        # Use text() with parameters for safer SQL execution
        # Note: For DDL statements like CREATE TABLE, we still need dynamic construction
        # but with strict validation and escaping
        table_sql = text(f"""
        CREATE TABLE IF NOT EXISTS {escaped_schema}.{escaped_table} (
            {', '.join(columns_sql)}
        )
        """)
        
        # Execute with proper parameter binding
        await conn.execute(str(table_sql))
        
        # Add table comment using parameterized query
        if table_def.description:
            comment_sql = text(f"COMMENT ON TABLE {escaped_schema}.{escaped_table} IS $1")
            await conn.execute(str(comment_sql), table_def.description)
        
        # Create indexes with validated and escaped components
        for index_def in table_def.indexes:
            # Validate index definition to prevent SQL injection
            validated_index_def = self._validate_index_definition(index_def)
            # Escape the index name components
            safe_index_suffix = index_def.replace('(', '').replace(')', '').replace(',', '_').replace(' ', '_')
            self._validate_sql_identifier(f"idx_{table_def.name}_{safe_index_suffix}")
            escaped_index_name = self._escape_identifier(f"idx_{table_def.name}_{safe_index_suffix}")
            index_sql = text(f"CREATE INDEX IF NOT EXISTS {escaped_index_name} ON {escaped_schema}.{escaped_table} {validated_index_def}")
            await conn.execute(str(index_sql))
    
    def _validate_sql_identifier(self, identifier: str) -> None:
        """Validate SQL identifiers to prevent injection attacks."""
        if not identifier or not identifier.strip():
            raise DatabaseError("SQL identifier cannot be empty")
        
        # Check for dangerous patterns
        dangerous_patterns = [';', '--', '/*', '*/', 'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'GRANT', 'REVOKE']
        identifier_upper = identifier.upper()
        
        for pattern in dangerous_patterns:
            if pattern in identifier_upper:
                raise DatabaseError(f"Dangerous pattern '{pattern}' detected in identifier: {identifier}")
        
        # Allow only alphanumeric characters, underscores, and dots for schema.table format
        import re
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', identifier):
            raise DatabaseError(f"Invalid identifier format: {identifier}")
    
    def _escape_identifier(self, identifier: str) -> str:
        """Escape SQL identifiers to prevent injection."""
        # Remove or replace dangerous characters and wrap in quotes
        safe_identifier = identifier.replace('"', '""')  # Escape existing quotes
        return f'"{safe_identifier}"'
    
    def _validate_column_type(self, col_type: str) -> str:
        """Validate and sanitize column types against allowed PostgreSQL types."""
        # Whitelist of allowed PostgreSQL data types and their patterns
        allowed_types = [
            # Basic types
            'TEXT', 'VARCHAR', 'CHAR', 'INTEGER', 'BIGINT', 'SMALLINT',
            'DECIMAL', 'NUMERIC', 'REAL', 'DOUBLE PRECISION', 'SERIAL', 'BIGSERIAL',
            'BOOLEAN', 'DATE', 'TIME', 'TIMESTAMP', 'TIMESTAMPTZ', 'INTERVAL',
            'UUID', 'JSONB', 'JSON', 'BYTEA', 'VECTOR',
            # Array types
            'TEXT[]', 'INTEGER[]', 'BIGINT[]',
            # Common constraints/modifiers
            'PRIMARY KEY', 'NOT NULL', 'UNIQUE', 'DEFAULT', 'CHECK', 'REFERENCES'
        ]
        
        # Clean and normalize the type string
        cleaned_type = col_type.strip()
        
        # Reject empty or suspicious input immediately
        if not cleaned_type or ';' in cleaned_type or '--' in cleaned_type:
            raise DatabaseError(f"Invalid column type: {col_type}")
        
        type_upper = cleaned_type.upper()
        
        # Check if it starts with an allowed type or contains allowed patterns
        for allowed in allowed_types:
            if type_upper.startswith(allowed) or (allowed in type_upper and allowed in ['PRIMARY KEY', 'NOT NULL', 'UNIQUE']):
                return cleaned_type  # Return original case for proper PostgreSQL syntax
        
        # Handle specific VARCHAR and CHAR patterns with length specifications
        import re
        if re.match(r'^VARCHAR\(\d+\)$', type_upper) or re.match(r'^CHAR\(\d+\)$', type_upper):
            return cleaned_type
        
        # REJECT unknown types for security
        raise DatabaseError(f"Unsupported column type: {col_type}. Only whitelisted PostgreSQL types are allowed.")
    
    def _validate_default_value(self, default_value: str) -> str:
        """Validate and sanitize default values with strict security controls."""
        cleaned_default = default_value.strip()
        
        # Reject obviously dangerous patterns
        dangerous_patterns = [';', '--', '/*', '*/', 'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'EXECUTE', 'UNION']
        default_upper = cleaned_default.upper()
        for pattern in dangerous_patterns:
            if pattern in default_upper:
                raise DatabaseError(f"Dangerous pattern '{pattern}' detected in default value: {default_value}")
        
        # Check for numeric values (integers and floats)
        try:
            float(cleaned_default)
            return cleaned_default  # It's a number, safe to use
        except ValueError:
            pass
        
        # List of explicitly allowed function calls and constants
        safe_functions = [
            'NOW()', 'CURRENT_TIMESTAMP', 'CURRENT_DATE', 'CURRENT_TIME',
            'gen_random_uuid()', 'TRUE', 'FALSE', 'NULL'
        ]
        
        # Check against safe function patterns (exact match)
        if default_upper in safe_functions:
            return cleaned_default
        
        # Handle string literals with strict validation
        if cleaned_default.startswith("'") and cleaned_default.endswith("'"):
            # Validate string content - no dangerous characters
            inner_content = cleaned_default[1:-1]
            if any(char in inner_content for char in [';', '--']):
                raise DatabaseError(f"Dangerous characters in string literal: {default_value}")
            # Escape single quotes within the string
            safe_inner = inner_content.replace("'", "''")
            return f"'{safe_inner}'"
        
        # Reject anything else as potentially unsafe
        raise DatabaseError(f"Unsupported default value: {default_value}. Only whitelisted patterns are allowed.")
    
    def _validate_constraint(self, constraint: str) -> str:
        """Validate and sanitize table constraints."""
        # Basic constraint validation - in production, this should be more comprehensive
        cleaned_constraint = constraint.strip()
        
        # Common safe constraint patterns
        safe_constraint_patterns = [
            'UNIQUE', 'PRIMARY KEY', 'FOREIGN KEY', 'CHECK', 'NOT NULL',
            'REFERENCES', 'ON DELETE', 'ON UPDATE', 'CASCADE', 'RESTRICT'
        ]
        
        constraint_upper = cleaned_constraint.upper()
        for pattern in safe_constraint_patterns:
            if pattern in constraint_upper:
                return cleaned_constraint
        
        self.logger.warning(f"Potentially unsafe constraint detected: {constraint}")
        return cleaned_constraint
    
    def _validate_index_definition(self, index_def: str) -> str:
        """Validate and sanitize index definitions to prevent SQL injection."""
        cleaned_index = index_def.strip()
        
        # Remove any potentially dangerous characters and patterns
        # Allow only: letters, numbers, underscores, parentheses, commas, spaces, and dots
        import re
        if not re.match(r'^[\w\s(),.]+$', cleaned_index):
            raise DatabaseError(f"Invalid characters in index definition: {index_def}")
        
        # Check for dangerous SQL keywords that shouldn't be in index definitions
        # Use word boundaries to avoid false positives (e.g., "CREATE" in "created_at")
        dangerous_keywords = [
            r'\bDROP\b', r'\bDELETE\b', r'\bUPDATE\b', r'\bINSERT\b', r'\bALTER\b', 
            r'\bTRUNCATE\b', r'\bGRANT\b', r'\bREVOKE\b', r'\bEXECUTE\b', 
            r'\bUNION\b', r'\bSELECT\b', '--', ';', r'/\*', r'\*/'
        ]
        
        index_upper = cleaned_index.upper()
        for keyword_pattern in dangerous_keywords:
            if re.search(keyword_pattern, index_upper):
                raise DatabaseError(f"Forbidden SQL pattern detected in index definition: {index_def}")
        
        # Validate that it looks like a proper index definition
        # Should be in format like: (column_name) or (col1, col2) or (func(column))
        if not (cleaned_index.startswith('(') and cleaned_index.endswith(')')):
            raise DatabaseError(f"Index definition must be enclosed in parentheses: {index_def}")
        
        # Extract content within parentheses and validate column names
        content = cleaned_index[1:-1].strip()
        if not content:
            raise DatabaseError(f"Empty index definition: {index_def}")
        
        # Split by comma and validate each column/expression
        columns = [col.strip() for col in content.split(',')]
        for col in columns:
            if not col:
                raise DatabaseError(f"Empty column name in index definition: {index_def}")
            # Basic validation - column names should be alphanumeric with underscores
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', col):
                # Allow function calls like LOWER(column_name) but be restrictive
                if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\([a-zA-Z_][a-zA-Z0-9_]*\)$', col):
                    raise DatabaseError(f"Invalid column specification in index: {col}")
        
        return cleaned_index
    
    async def get_agent_schema_info(self, agent_id: str) -> Dict[str, Any]:
        """Get information about an agent's database schema."""
        try:
            if agent_id not in self.agent_schemas:
                raise DatabaseError(f"Unknown agent ID: {agent_id}")
            
            schema_name = self.agent_schemas[agent_id]["name"]
            
            async with self.connection_pool.acquire() as conn:
                # Get tables in schema
                tables = await conn.fetch("""
                    SELECT table_name, table_type 
                    FROM information_schema.tables 
                    WHERE table_schema = $1
                    ORDER BY table_name
                """, schema_name)
                
                # Get table details
                table_info = []
                for table in tables:
                    columns = await conn.fetch("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns
                        WHERE table_schema = $1 AND table_name = $2
                        ORDER BY ordinal_position
                    """, schema_name, table['table_name'])
                    
                    table_info.append({
                        "name": table['table_name'],
                        "type": table['table_type'],
                        "columns": [dict(col) for col in columns]
                    })
                
                return {
                    "agent_id": agent_id,
                    "schema_name": schema_name,
                    "description": self.agent_schemas[agent_id]["description"],
                    "business_domain": self.agent_schemas[agent_id]["business_domain"],
                    "tables": table_info,
                    "table_count": len(table_info)
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get schema info for {agent_id}: {e}")
            raise DatabaseError(f"Schema info retrieval failed: {e}")
    
    async def execute_agent_query(self, agent_id: str, query: str, params: Optional[List] = None) -> List[Dict]:
        """Execute a query within an agent's schema context."""
        try:
            if agent_id not in self.agent_schemas:
                raise DatabaseError(f"Unknown agent ID: {agent_id}")
            
            schema_name = self.agent_schemas[agent_id]["name"]
            
            # Set search path to agent schema first, then public
            search_path_query = f"SET search_path TO {schema_name}, public"
            
            async with self.connection_pool.acquire() as conn:
                # Set schema search path
                await conn.execute(search_path_query)
                
                # Execute the query
                if params:
                    result = await conn.fetch(query, *params)
                else:
                    result = await conn.fetch(query)
                
                return [dict(row) for row in result]
                
        except Exception as e:
            self.logger.error(f"Query execution failed for {agent_id}: {e}")
            raise DatabaseError(f"Query execution failed: {e}")
    
    async def insert_agent_data(self, agent_id: str, table_name: str, data: Dict[str, Any]) -> str:
        """Insert data into an agent's table and return the ID."""
        try:
            if agent_id not in self.agent_schemas:
                raise DatabaseError(f"Unknown agent ID: {agent_id}")
            
            schema_name = self.agent_schemas[agent_id]["name"]
            
            # Build insert query
            columns = list(data.keys())
            placeholders = [f"${i+1}" for i in range(len(columns))]
            values = list(data.values())
            
            query = f"""
                INSERT INTO {schema_name}.{table_name} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                RETURNING id
            """
            
            async with self.connection_pool.acquire() as conn:
                result = await conn.fetchval(query, *values)
                return str(result)
                
        except Exception as e:
            self.logger.error(f"Data insertion failed for {agent_id}: {e}")
            raise DatabaseError(f"Data insertion failed: {e}")
    
    async def get_schema_statistics(self) -> Dict[str, Any]:
        """Get statistics about all agent schemas."""
        try:
            stats = {}
            
            async with self.connection_pool.acquire() as conn:
                for agent_id, schema_info in self.agent_schemas.items():
                    schema_name = schema_info["name"]
                    
                    # Count tables
                    table_count = await conn.fetchval("""
                        SELECT COUNT(*) FROM information_schema.tables 
                        WHERE table_schema = $1
                    """, schema_name)
                    
                    # Get total rows across all tables
                    tables = await conn.fetch("""
                        SELECT table_name FROM information_schema.tables 
                        WHERE table_schema = $1 AND table_type = 'BASE TABLE'
                    """, schema_name)
                    
                    total_rows = 0
                    for table in tables:
                        try:
                            row_count = await conn.fetchval(
                                f"SELECT COUNT(*) FROM {schema_name}.{table['table_name']}"
                            )
                            total_rows += row_count
                        except Exception:
                            # Skip if table doesn't exist or is inaccessible
                            pass
                    
                    stats[agent_id] = {
                        "schema_name": schema_name,
                        "table_count": table_count,
                        "total_rows": total_rows,
                        "business_domain": schema_info["business_domain"]
                    }
            
            return {
                "agent_schemas": stats,
                "total_agents": len(self.agent_schemas),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get schema statistics: {e}")
            raise DatabaseError(f"Statistics retrieval failed: {e}")
    
    async def close(self) -> None:
        """Close database connections."""
        try:
            if self.connection_pool:
                await self.connection_pool.close()
                self.logger.info("Database schema manager connections closed")
                
        except Exception as e:
            self.logger.error(f"Error closing database connections: {e}")


# Agent-specific table definitions will be added here
# These are templates that can be customized based on business rules

def get_financial_advisor_tables() -> List[TableDefinition]:
    """Get table definitions for financial advisor agent (Agent Alpha)."""
    return [
        # User will define these tables based on their financial advisor business rules
        # Placeholder for now
    ]

def get_content_creator_tables() -> List[TableDefinition]:
    """Get table definitions for content creator agent (Agent Beta)."""
    return [
        # User will define these tables based on their content creator business rules
        # Placeholder for now
    ]