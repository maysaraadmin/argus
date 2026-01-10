#!/usr/bin/env python3
import click
import uvicorn
from pathlib import Path
import sys

@click.group()
def cli():
    """Argus MVP - Open Source Intelligence Platform"""
    pass

@cli.command()
def init():
    """Initialize Argus database"""
    from alembic.config import Config
    from alembic import command
    
    # Create config directory
    config_dir = Path.home() / ".argus"
    config_dir.mkdir(exist_ok=True)
    
    click.echo("Initializing Argus database...")
    
    # Run migrations
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    
    click.echo("✅ Database initialized")

@cli.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
def serve(host, port):
    """Start the API server"""
    click.echo(f"🚀 Starting Argus API on {host}:{port}")
    uvicorn.run(
        "src.api.server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--type", default="csv", help="Data type: csv, json, excel")
def import_data(filepath, type):
    """Import data from file"""
    from src.core.importer import DataImporter
    
    importer = DataImporter()
    result = importer.import_file(filepath, file_type=type)
    
    click.echo(f"✅ Imported {result['entities']} entities")
    click.echo(f"✅ Created {result['relationships']} relationships")

@cli.command()
@click.argument("entity1")
@click.argument("entity2")
@click.option("--depth", default=3, help="Max search depth")
def find_connection(entity1, entity2, depth):
    """Find connections between two entities"""
    from src.core.graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    paths = kg.find_connections(entity1, entity2, max_depth=depth)
    
    if paths:
        click.echo(f"🔗 Found {len(paths)} connection(s):")
        for i, path in enumerate(paths, 1):
            click.echo(f"\nPath {i}:")
            click.echo(" → ".join(path))
    else:
        click.echo("❌ No connection found")

if __name__ == "__main__":
    cli()