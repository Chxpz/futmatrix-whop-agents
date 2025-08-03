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
        """Create a single table with all its components."""
        # Build column definitions
        columns_sql = []
        for col in table_def.columns:
            col_def = f"{col['name']} {col['type']}"
            if col.get('primary_key'):
                col_def += " PRIMARY KEY"
            if col.get('not_null'):
                col_def += " NOT NULL"
            if col.get('default'):
                col_def += f" DEFAULT {col['default']}"
            if col.get('unique'):
                col_def += " UNIQUE"
            columns_sql.append(col_def)
        
        # Add constraints
        if table_def.constraints:
            columns_sql.extend(table_def.constraints)
        
        # Create table SQL
        table_sql = f"""
        CREATE TABLE IF NOT EXISTS {schema_name}.{table_def.name} (
            {', '.join(columns_sql)}
        )
        """
        
        await conn.execute(table_sql)
        
        # Add table comment
        if table_def.description:
            await conn.execute(
                f"COMMENT ON TABLE {schema_name}.{table_def.name} IS $1",
                table_def.description
            )
        
        # Create indexes
        for index_def in table_def.indexes:
            index_name = f"idx_{table_def.name}_{index_def.replace('(', '').replace(')', '').replace(',', '_').replace(' ', '_')}"
            index_sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {schema_name}.{table_def.name} {index_def}"
            await conn.execute(index_sql)
    
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