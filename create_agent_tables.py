"""
Script to create agent-specific database tables.
Run this after setting up the Docker services to initialize agent schemas.
"""
import asyncio
import logging
from table_definitions_template import (
    get_financial_advisor_tables,
    get_content_creator_tables,
    get_general_tables
)
from core.database_schema import DatabaseSchemaManager
from config.settings import Settings
from utils.logger import setup_logger

async def create_all_agent_tables():
    """Create tables for all agents based on their business rules."""
    setup_logger()
    logger = logging.getLogger("create_agent_tables")
    
    try:
        logger.info("Starting agent table creation process...")
        
        # Initialize settings and schema manager
        settings = Settings()
        schema_manager = DatabaseSchemaManager(settings)
        
        # Initialize connection
        await schema_manager.initialize()
        logger.info("Database schema manager initialized")
        
        # Create tables for Agent Alpha (Financial Advisor)
        logger.info("Creating tables for Agent Alpha (Financial Advisor)...")
        alpha_tables = get_financial_advisor_tables()
        if alpha_tables:
            await schema_manager.create_agent_tables("agent_alpha", alpha_tables)
            logger.info(f"Created {len(alpha_tables)} tables for Agent Alpha")
        else:
            logger.info("No tables defined for Agent Alpha - using template placeholders")
        
        # Create tables for Agent Beta (Content Creator)
        logger.info("Creating tables for Agent Beta (Content Creator)...")
        beta_tables = get_content_creator_tables()
        if beta_tables:
            await schema_manager.create_agent_tables("agent_beta", beta_tables)
            logger.info(f"Created {len(beta_tables)} tables for Agent Beta")
        else:
            logger.info("No tables defined for Agent Beta - using template placeholders")
        
        # Create general shared tables
        logger.info("Creating general shared tables...")
        general_tables = get_general_tables()
        if general_tables:
            # General tables go in public schema, but we need to handle them differently
            for table_def in general_tables:
                # Create in public schema
                async with schema_manager.connection_pool.acquire() as conn:
                    await schema_manager._create_table(conn, table_def, "public")
            logger.info(f"Created {len(general_tables)} general tables")
        
        # Display schema information
        logger.info("\n=== Agent Schema Summary ===")
        
        for agent_id in ["agent_alpha", "agent_beta"]:
            try:
                schema_info = await schema_manager.get_agent_schema_info(agent_id)
                logger.info(f"\n{schema_info['description']}:")
                logger.info(f"  Schema: {schema_info['schema_name']}")
                logger.info(f"  Tables: {schema_info['table_count']}")
                for table in schema_info['tables']:
                    logger.info(f"    - {table['name']} ({len(table['columns'])} columns)")
            except Exception as e:
                logger.warning(f"Could not get schema info for {agent_id}: {e}")
        
        # Display statistics
        stats = await schema_manager.get_schema_statistics()
        logger.info(f"\n=== Database Statistics ===")
        logger.info(f"Total agent schemas: {stats['total_agents']}")
        for agent_id, agent_stats in stats['agent_schemas'].items():
            logger.info(f"  {agent_id}: {agent_stats['table_count']} tables, {agent_stats['total_rows']} rows")
        
        logger.info("\n=== Table Creation Complete ===")
        logger.info("Your agents now have dedicated database schemas!")
        logger.info("Next steps:")
        logger.info("1. Customize the table definitions in table_definitions_template.py")
        logger.info("2. Re-run this script to update the database schema")
        logger.info("3. Start the agents system with: python start_system.py")
        
        await schema_manager.close()
        
    except Exception as e:
        logger.error(f"Table creation failed: {e}")
        if "connection" in str(e).lower():
            logger.error("Make sure the database is running: docker-compose up -d")
        raise

if __name__ == "__main__":
    asyncio.run(create_all_agent_tables())