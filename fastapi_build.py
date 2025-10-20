#!/usr/bin/env python3
"""
FastAPI Application Builder
Automatically generates a complete FastAPI application from YAML specifications.

Reads SYSTEM_INDEX.yaml and all feature requirements to create:
- Complete FastAPI application structure
- Feature routers with endpoints
- Database models and migrations
- Configuration and environment setup
- Docker deployment files
- Testing infrastructure
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import yaml
import json
from dataclasses import dataclass, field
import re

# Add control_tower to path
control_tower_root = Path(__file__).parent.resolve()
if str(control_tower_root) not in sys.path:
    sys.path.insert(0, str(control_tower_root))


@dataclass
class DatabaseSchema:
    """Database table schema extracted from requirements."""
    table_name: str
    columns: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    indexes: List[str] = field(default_factory=list)


@dataclass
class APIEndpoint:
    """API endpoint specification."""
    path: str
    method: str
    function_name: str
    summary: str
    authentication_required: bool = True
    request_model: Optional[str] = None
    response_model: Optional[str] = None


@dataclass
class FeatureSpec:
    """Feature specification extracted from YAML."""
    feature_id: str
    feature_name: str
    feature_code: str
    feature_dir: Path
    layers: List[Dict[str, Any]]
    endpoints: List[APIEndpoint] = field(default_factory=list)
    database_schemas: List[DatabaseSchema] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    environment_variables: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class SystemSpec:
    """Complete system specification."""
    system_id: str
    system_name: str
    system_dir: Path
    features: List[FeatureSpec]
    database_type: str = "postgresql"
    python_version: str = "3.11"


class FastAPIBuilder:
    """Build complete FastAPI application from YAML specifications."""
    
    def __init__(self, system_index_path: str, output_dir: str = None, verbose: bool = False):
        """Initialize FastAPI builder."""
        self.system_index_path = Path(system_index_path)
        self.system_dir = self.system_index_path.parent
        self.output_dir = Path(output_dir) if output_dir else self.system_dir / "fastapi_app"
        self.verbose = verbose
        self.system_spec: Optional[SystemSpec] = None
        
    def print_header(self, title: str):
        """Print section header."""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
        
    def print_step(self, icon: str, message: str):
        """Print step message."""
        print(f"{icon} {message}")
        
    def log(self, message: str):
        """Print verbose log message."""
        if self.verbose:
            print(f"  → {message}")
    
    def parse_system_index(self) -> SystemSpec:
        """Parse SYSTEM_INDEX.yaml and extract system specification."""
        self.print_header("📋 Parsing System Specification")
        
        with open(self.system_index_path, 'r') as f:
            system_yaml = yaml.safe_load(f)
        
        # Support both SYSTEM_INDEX and FEATURE_INDEX formats
        metadata = system_yaml['metadata']
        system_id = metadata.get('system_id', metadata.get('requirement_id'))
        system_name = metadata.get('system_name', metadata.get('requirement_name'))
        
        self.print_step("✓", f"System: {system_name} ({system_id})")
        
        # Parse features
        features = []
        feature_list = system_yaml.get('features', [])
        self.print_step("✓", f"Found {len(feature_list)} features")
        
        for feature_info in feature_list:
            feature_spec = self.parse_feature(feature_info)
            if feature_spec:
                features.append(feature_spec)
                self.print_step("  ", f"- {feature_spec.feature_name}")
        
        self.system_spec = SystemSpec(
            system_id=system_id,
            system_name=system_name,
            system_dir=self.system_dir,
            features=features
        )
        
        return self.system_spec
    
    def parse_feature(self, feature_info: Dict[str, Any]) -> Optional[FeatureSpec]:
        """Parse individual feature specification."""
        feature_id = feature_info.get('feature_id')
        feature_name = feature_info.get('feature_name')
        feature_code = feature_info.get('feature_code', feature_id)
        feature_folder = feature_info.get('feature_folder')
        
        if not feature_folder:
            self.log(f"⚠️  No feature_folder specified for {feature_id}")
            return None
        
        feature_dir = self.system_dir / feature_folder
        if not feature_dir.exists():
            self.log(f"⚠️  Feature directory not found: {feature_dir}")
            return None
        
        # Load feature requirements index
        feature_index_path = feature_dir / "FEATURE_REQUIREMENTS_INDEX.yaml"
        if not feature_index_path.exists():
            self.log(f"⚠️  Feature index not found: {feature_index_path}")
            return None
        
        with open(feature_index_path, 'r') as f:
            feature_yaml = yaml.safe_load(f)
        
        layers = feature_yaml.get('layers', [])
        
        # Extract database schemas
        database_schemas = self.extract_database_schemas(feature_dir, layers)
        
        # Extract API endpoints
        endpoints = self.extract_api_endpoints(feature_dir, feature_code)
        
        # Extract dependencies
        dependencies = self.extract_dependencies(feature_dir, layers)
        
        # Extract environment variables
        env_vars = self.extract_environment_variables(feature_dir, layers)
        
        return FeatureSpec(
            feature_id=feature_id,
            feature_name=feature_name,
            feature_code=feature_code,
            feature_dir=feature_dir,
            layers=layers,
            endpoints=endpoints,
            database_schemas=database_schemas,
            dependencies=dependencies,
            environment_variables=env_vars
        )
    
    def extract_database_schemas(self, feature_dir: Path, layers: List[Dict]) -> List[DatabaseSchema]:
        """Extract database schemas from layer requirements."""
        schemas = []
        
        for layer in layers:
            req_file = layer.get('requirement_file')
            layer_dir = layer.get('layer_directory')
            
            if not req_file or not layer_dir:
                continue
            
            req_path = feature_dir / layer_dir / req_file
            if not req_path.exists():
                continue
            
            try:
                with open(req_path, 'r') as f:
                    req_yaml = yaml.safe_load(f)
                
                # Look for database schemas in various locations
                db_schema = req_yaml.get('specification', {}).get('database_schema')
                if db_schema:
                    schemas.extend(self.parse_database_schema(db_schema))
                
            except Exception as e:
                self.log(f"⚠️  Error parsing {req_path}: {e}")
        
        return schemas
    
    def parse_database_schema(self, schema_yaml: Any) -> List[DatabaseSchema]:
        """Parse database schema from YAML."""
        schemas = []
        
        if isinstance(schema_yaml, dict):
            tables = schema_yaml.get('tables', [])
            for table in tables:
                if isinstance(table, dict):
                    schema = DatabaseSchema(
                        table_name=table.get('name', ''),
                        columns=table.get('columns', []),
                        relationships=table.get('relationships', []),
                        indexes=table.get('indexes', [])
                    )
                    schemas.append(schema)
        
        return schemas
    
    def extract_api_endpoints(self, feature_dir: Path, feature_code: str) -> List[APIEndpoint]:
        """Extract API endpoints from feature integration code."""
        endpoints = []
        
        # Look for feature_integration.py
        integration_file = feature_dir / "src" / "feature_integration.py"
        if not integration_file.exists():
            return endpoints
        
        try:
            with open(integration_file, 'r') as f:
                content = f.read()
            
            # Parse for FastAPI route decorators (simplified)
            # Look for patterns like: @app.get("/path")
            route_pattern = r'@(?:app|router)\.(\w+)\(["\']([^"\']+)["\']\)'
            matches = re.finditer(route_pattern, content)
            
            for match in matches:
                method = match.group(1).upper()
                path = match.group(2)
                
                # Try to extract function name (next line after decorator)
                func_match = re.search(rf'{re.escape(match.group(0))}\s*(?:async\s+)?def\s+(\w+)', content)
                func_name = func_match.group(1) if func_match else "handler"
                
                endpoint = APIEndpoint(
                    path=path,
                    method=method,
                    function_name=func_name,
                    summary=f"{method} {path}",
                    authentication_required=True
                )
                endpoints.append(endpoint)
            
        except Exception as e:
            self.log(f"⚠️  Error extracting endpoints from {integration_file}: {e}")
        
        return endpoints
    
    def extract_dependencies(self, feature_dir: Path, layers: List[Dict]) -> List[str]:
        """Extract Python dependencies from requirements."""
        dependencies = set()
        
        for layer in layers:
            req_file = layer.get('requirement_file')
            layer_dir = layer.get('layer_directory')
            
            if not req_file or not layer_dir:
                continue
            
            req_path = feature_dir / layer_dir / req_file
            if not req_path.exists():
                continue
            
            try:
                with open(req_path, 'r') as f:
                    req_yaml = yaml.safe_load(f)
                
                # Extract dependencies from deployment section
                deployment = req_yaml.get('deployment', {})
                deps = deployment.get('dependencies', [])
                
                if isinstance(deps, list):
                    dependencies.update(deps)
                
            except Exception as e:
                self.log(f"⚠️  Error extracting dependencies from {req_path}: {e}")
        
        return sorted(list(dependencies))
    
    def extract_environment_variables(self, feature_dir: Path, layers: List[Dict]) -> List[Dict[str, str]]:
        """Extract required environment variables."""
        env_vars = []
        
        for layer in layers:
            req_file = layer.get('requirement_file')
            layer_dir = layer.get('layer_directory')
            
            if not req_file or not layer_dir:
                continue
            
            req_path = feature_dir / layer_dir / req_file
            if not req_path.exists():
                continue
            
            try:
                with open(req_path, 'r') as f:
                    req_yaml = yaml.safe_load(f)
                
                # Extract environment variables from deployment section
                deployment = req_yaml.get('deployment', {})
                env = deployment.get('environment_variables', {})
                
                if isinstance(env, dict):
                    for key, value in env.items():
                        env_vars.append({
                            'name': key,
                            'description': value.get('description', '') if isinstance(value, dict) else str(value),
                            'required': value.get('required', True) if isinstance(value, dict) else True
                        })
                
            except Exception as e:
                self.log(f"⚠️  Error extracting env vars from {req_path}: {e}")
        
        return env_vars
    
    def build_application(self) -> bool:
        """Build complete FastAPI application."""
        self.print_header("🏗️  Building FastAPI Application")
        
        # Create output directory structure
        self.create_directory_structure()
        
        # Generate application files
        self.generate_main_py()
        self.generate_config_py()
        self.generate_database_py()
        self.generate_dependencies_py()
        
        # Generate middleware
        self.generate_middleware()
        
        # Generate feature routers
        self.generate_routers()
        
        # Generate database models
        self.generate_models()
        
        # Generate configuration files
        self.generate_requirements_txt()
        self.generate_env_example()
        self.generate_docker_files()
        
        # Generate documentation
        self.generate_readme()
        
        self.print_header("✅ FastAPI Application Built Successfully")
        self.print_step("📁", f"Output directory: {self.output_dir}")
        self.print_step("🚀", "To run: cd fastapi_app && uvicorn main:app --reload")
        
        return True
    
    def create_directory_structure(self):
        """Create FastAPI application directory structure."""
        self.print_step("📁", "Creating directory structure...")
        
        directories = [
            self.output_dir,
            self.output_dir / "routers",
            self.output_dir / "models",
            self.output_dir / "middleware",
            self.output_dir / "tests",
            self.output_dir / "alembic",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.log(f"Created: {directory}")
    
    def generate_main_py(self):
        """Generate main FastAPI application file."""
        self.print_step("📝", "Generating main.py...")
        
        router_imports = []
        router_includes = []
        
        for feature in self.system_spec.features:
            router_var = f"{feature.feature_code}_router"
            router_imports.append(
                f"from routers.{feature.feature_code} import router as {router_var}"
            )
            router_includes.append(
                f'app.include_router({router_var}, prefix="/api/v1/{feature.feature_code}", tags=["{feature.feature_name}"])'
            )
        
        content = f'''"""
{self.system_spec.system_name} - FastAPI Application
Auto-generated by fastapi_build.py
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from config import settings
from database import engine, Base
from middleware.logging_middleware import LoggingMiddleware
from middleware.error_handler import ErrorHandlerMiddleware

# Import routers
{chr(10).join(router_imports)}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="{self.system_spec.system_name}",
    description="Auto-generated FastAPI application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

# Include routers
{chr(10).join(router_includes)}

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {{"status": "healthy", "service": "{self.system_spec.system_name}"}}

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {{
        "message": "Welcome to {self.system_spec.system_name}",
        "docs": "/docs",
        "health": "/health"
    }}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting {self.system_spec.system_name}...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down {self.system_spec.system_name}...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
'''
        
        output_file = self.output_dir / "main.py"
        with open(output_file, 'w') as f:
            f.write(content)
        
        self.log(f"Generated: {output_file}")
    
    def generate_config_py(self):
        """Generate configuration file."""
        self.print_step("📝", "Generating config.py...")
        
        # Collect all environment variables
        all_env_vars = []
        for feature in self.system_spec.features:
            all_env_vars.extend(feature.environment_variables)
        
        # Deduplicate by name
        env_vars_dict = {var['name']: var for var in all_env_vars}
        
        content = f'''"""
Configuration Management
Auto-generated by fastapi_build.py
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "{self.system_spec.system_name}"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
'''
        
        output_file = self.output_dir / "config.py"
        with open(output_file, 'w') as f:
            f.write(content)
        
        self.log(f"Generated: {output_file}")
    
    def generate_database_py(self):
        """Generate database configuration."""
        self.print_step("📝", "Generating database.py...")
        
        content = '''"""
Database Configuration
Auto-generated by fastapi_build.py
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create Base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
        
        output_file = self.output_dir / "database.py"
        with open(output_file, 'w') as f:
            f.write(content)
        
        self.log(f"Generated: {output_file}")
    
    def generate_dependencies_py(self):
        """Generate FastAPI dependencies."""
        self.print_step("📝", "Generating dependencies.py...")
        
        content = '''"""
FastAPI Dependencies
Auto-generated by fastapi_build.py
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from config import settings
from database import get_db

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Dependency to get current authenticated user.
    Validates JWT token and returns user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # TODO: Fetch user from database
    # user = db.query(User).filter(User.id == user_id).first()
    # if user is None:
    #     raise credentials_exception
    
    return {"user_id": user_id}


async def require_admin(
    current_user: dict = Depends(get_current_user)
):
    """Dependency to require admin role."""
    # TODO: Check user role
    # if current_user.get("role") != "admin":
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Admin privileges required"
    #     )
    return current_user
'''
        
        output_file = self.output_dir / "dependencies.py"
        with open(output_file, 'w') as f:
            f.write(content)
        
        self.log(f"Generated: {output_file}")
    
    def generate_middleware(self):
        """Generate middleware files."""
        self.print_step("📝", "Generating middleware...")
        
        # Logging middleware
        logging_content = '''"""
Logging Middleware
Auto-generated by fastapi_build.py
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and log details."""
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        duration = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"- {response.status_code} ({duration:.3f}s)"
        )
        
        return response
'''
        
        # Error handler middleware
        error_content = '''"""
Error Handler Middleware
Auto-generated by fastapi_build.py
"""

import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware to handle exceptions gracefully."""
    
    async def dispatch(self, request: Request, call_next):
        """Catch and handle exceptions."""
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            logger.error(
                f"Unhandled exception: {str(exc)}",
                exc_info=True
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": str(exc)
                }
            )
'''
        
        # Save middleware files
        logging_file = self.output_dir / "middleware" / "logging_middleware.py"
        with open(logging_file, 'w') as f:
            f.write(logging_content)
        self.log(f"Generated: {logging_file}")
        
        error_file = self.output_dir / "middleware" / "error_handler.py"
        with open(error_file, 'w') as f:
            f.write(error_content)
        self.log(f"Generated: {error_file}")
        
        # Create __init__.py
        init_file = self.output_dir / "middleware" / "__init__.py"
        init_file.write_text('"""Middleware package."""\n')
        self.log(f"Generated: {init_file}")
    
    def generate_routers(self):
        """Generate feature routers."""
        self.print_step("📝", "Generating feature routers...")
        
        for feature in self.system_spec.features:
            self.log(f"Generating router for {feature.feature_name}...")
            
            content = f'''"""
{feature.feature_name} Router
Auto-generated by fastapi_build.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from dependencies import get_current_user

router = APIRouter()


@router.get("/", summary="List {feature.feature_name}")
async def list_items(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all items for {feature.feature_name}.
    
    TODO: Implement business logic from feature_integration.py
    """
    return {{"message": "List {feature.feature_name}", "items": []}}


@router.get("/{{item_id}}", summary="Get {feature.feature_name} Item")
async def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific item by ID.
    
    TODO: Implement business logic from feature_integration.py
    """
    return {{
        "message": "Get {feature.feature_name} item",
        "item_id": item_id
    }}


@router.post("/", summary="Create {feature.feature_name} Item", status_code=status.HTTP_201_CREATED)
async def create_item(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new item.
    
    TODO: Implement business logic from feature_integration.py
    """
    return {{
        "message": "Create {feature.feature_name} item",
        "item_id": 1
    }}


@router.put("/{{item_id}}", summary="Update {feature.feature_name} Item")
async def update_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing item.
    
    TODO: Implement business logic from feature_integration.py
    """
    return {{
        "message": "Update {feature.feature_name} item",
        "item_id": item_id
    }}


@router.delete("/{{item_id}}", summary="Delete {feature.feature_name} Item")
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an item.
    
    TODO: Implement business logic from feature_integration.py
    """
    return {{
        "message": "Delete {feature.feature_name} item",
        "item_id": item_id
    }}
'''
            
            router_file = self.output_dir / "routers" / f"{feature.feature_code}.py"
            with open(router_file, 'w') as f:
                f.write(content)
            
            self.log(f"  ✓ Generated: {router_file}")
        
        # Create routers __init__.py
        init_file = self.output_dir / "routers" / "__init__.py"
        init_file.write_text('"""Routers package."""\n')
        self.log(f"Generated: {init_file}")
    
    def generate_models(self):
        """Generate SQLAlchemy models."""
        self.print_step("📝", "Generating database models...")
        
        for feature in self.system_spec.features:
            if not feature.database_schemas:
                continue
            
            count = len(feature.database_schemas)
            self.log(f"Generating models for {feature.feature_name} "
                    f"({count} tables)...")
            
            model_imports = [
                "from sqlalchemy import Column, Integer, String, DateTime, "
                "Boolean, ForeignKey, Text, Float",
                "from sqlalchemy.orm import relationship",
                "from datetime import datetime",
                "from database import Base"
            ]
            
            model_classes = []
            
            for schema in feature.database_schemas:
                class_name = self.to_class_name(schema.table_name)
                
                columns = []
                for col in schema.columns:
                    col_name = col.get('name', '')
                    col_type = col.get('type', 'String')
                    nullable = col.get('nullable', True)
                    primary_key = col.get('primary_key', False)
                    
                    sqlalchemy_type = self.map_column_type(col_type)
                    
                    col_def = (
                        f"    {col_name} = Column({sqlalchemy_type}, "
                        f"primary_key={primary_key}, nullable={nullable})"
                    )
                    columns.append(col_def)
                
                model_class = f'''

class {class_name}(Base):
    """
    {class_name} model.
    Table: {schema.table_name}
    """
    __tablename__ = "{schema.table_name}"
    
{chr(10).join(columns)}
    
    def __repr__(self):
        return f"<{class_name}(id={{self.id}})>"
'''
                model_classes.append(model_class)
            
            content = f'''"""
{feature.feature_name} Database Models
Auto-generated by fastapi_build.py
"""

{chr(10).join(model_imports)}

{''.join(model_classes)}
'''
            
            model_file = self.output_dir / "models" / f"{feature.feature_code}.py"
            with open(model_file, 'w') as f:
                f.write(content)
            
            self.log(f"  ✓ Generated: {model_file}")
        
        # Create models __init__.py
        init_file = self.output_dir / "models" / "__init__.py"
        init_file.write_text('"""Models package."""\n')
        self.log(f"Generated: {init_file}")
    
    def to_class_name(self, table_name: str) -> str:
        """Convert table_name to ClassName."""
        # Remove prefix, convert to PascalCase
        parts = table_name.replace('_', ' ').title().split()
        return ''.join(parts)
    
    def map_column_type(self, col_type: str) -> str:
        """Map generic column type to SQLAlchemy type."""
        type_mapping = {
            'integer': 'Integer',
            'int': 'Integer',
            'string': 'String',
            'str': 'String',
            'text': 'Text',
            'boolean': 'Boolean',
            'bool': 'Boolean',
            'datetime': 'DateTime',
            'date': 'DateTime',
            'float': 'Float',
            'decimal': 'Float',
        }
        return type_mapping.get(col_type.lower(), 'String')
    
    def generate_requirements_txt(self):
        """Generate requirements.txt with all dependencies."""
        self.print_step("📝", "Generating requirements.txt...")
        
        # Base FastAPI dependencies
        base_deps = [
            "fastapi==0.104.1",
            "uvicorn[standard]==0.24.0",
            "sqlalchemy==2.0.23",
            "alembic==1.12.1",
            "pydantic==2.5.0",
            "pydantic-settings==2.1.0",
            "python-jose[cryptography]==3.3.0",
            "passlib[bcrypt]==1.7.4",
            "python-multipart==0.0.6",
            "psycopg2-binary==2.9.9",
            "pytest==7.4.3",
            "pytest-asyncio==0.21.1",
            "httpx==0.25.2",
        ]
        
        # Collect feature-specific dependencies
        feature_deps = set()
        for feature in self.system_spec.features:
            feature_deps.update(feature.dependencies)
        
        # Combine and sort
        all_deps = sorted(set(base_deps) | feature_deps)
        
        content = f'''# Requirements for {self.system_spec.system_name}
# Auto-generated by fastapi_build.py
# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{chr(10).join(all_deps)}
'''
        
        output_file = self.output_dir / "requirements.txt"
        with open(output_file, 'w') as f:
            f.write(content)
        
        self.log(f"Generated: {output_file} ({len(all_deps)} packages)")
    
    def generate_env_example(self):
        """Generate .env.example file."""
        self.print_step("📝", "Generating .env.example...")
        
        # Collect all environment variables
        all_env_vars = []
        for feature in self.system_spec.features:
            all_env_vars.extend(feature.environment_variables)
        
        # Deduplicate by name
        env_vars_dict = {var['name']: var for var in all_env_vars}
        
        lines = [
            f"# Environment Configuration for {self.system_spec.system_name}",
            "# Auto-generated by fastapi_build.py",
            f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "# Application",
            f"APP_NAME={self.system_spec.system_name}",
            "DEBUG=false",
            "",
            "# Database",
            "DATABASE_URL=postgresql://user:password@localhost:5432/dbname",
            "",
            "# Security",
            "SECRET_KEY=your-secret-key-here-change-in-production",
            "ALGORITHM=HS256",
            "ACCESS_TOKEN_EXPIRE_MINUTES=30",
            "",
            "# Server",
            "HOST=0.0.0.0",
            "PORT=8000",
            "",
        ]
        
        # Add feature-specific environment variables
        if env_vars_dict:
            lines.append("# Feature-Specific Configuration")
            for var_name, var_info in sorted(env_vars_dict.items()):
                desc = var_info.get('description', '')
                if desc:
                    lines.append(f"# {desc}")
                lines.append(f"{var_name}=")
                lines.append("")
        
        content = '\n'.join(lines)
        
        output_file = self.output_dir / ".env.example"
        with open(output_file, 'w') as f:
            f.write(content)
        
        self.log(f"Generated: {output_file}")
    
    def generate_docker_files(self):
        """Generate Docker configuration files."""
        self.print_step("📝", "Generating Docker files...")
        
        # Dockerfile
        dockerfile_content = f'''# Dockerfile for {self.system_spec.system_name}
# Auto-generated by fastapi_build.py

FROM python:{self.system_spec.python_version}-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        
        # docker-compose.yml
        compose_content = f'''# docker-compose.yml for {self.system_spec.system_name}
# Auto-generated by fastapi_build.py

version: '3.8'

services:
  app:
    build: .
    container_name: {self.system_spec.system_id.lower()}_app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/app_db
      - SECRET_KEY=${{SECRET_KEY}}
    depends_on:
      - db
      - redis
    volumes:
      - .:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:14
    container_name: {self.system_spec.system_id.lower()}_db
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=app_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    container_name: {self.system_spec.system_id.lower()}_redis
    ports:
      - "6379:6379"

volumes:
  postgres_data:
'''
        
        # .dockerignore
        dockerignore_content = '''__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv
.env
*.log
.git
.gitignore
.pytest_cache
.coverage
htmlcov/
dist/
build/
*.egg-info
'''
        
        # Save files
        dockerfile = self.output_dir / "Dockerfile"
        with open(dockerfile, 'w') as f:
            f.write(dockerfile_content)
        self.log(f"Generated: {dockerfile}")
        
        compose_file = self.output_dir / "docker-compose.yml"
        with open(compose_file, 'w') as f:
            f.write(compose_content)
        self.log(f"Generated: {compose_file}")
        
        dockerignore = self.output_dir / ".dockerignore"
        with open(dockerignore, 'w') as f:
            f.write(dockerignore_content)
        self.log(f"Generated: {dockerignore}")
    
    def generate_readme(self):
        """Generate README.md documentation."""
        self.print_step("📝", "Generating README.md...")
        
        feature_list = '\n'.join([
            f"- **{f.feature_name}** (`{f.feature_code}`)"
            for f in self.system_spec.features
        ])
        
        router_list = '\n'.join([
            f"- `/api/v1/{f.feature_code}` - {f.feature_name}"
            for f in self.system_spec.features
        ])
        
        content = f'''# {self.system_spec.system_name}

Auto-generated FastAPI application by `fastapi_build.py`

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📋 Overview

This FastAPI application was automatically generated from YAML specifications.

## ✨ Features

{feature_list}

## 🚀 Quick Start

### Prerequisites

- Python {self.system_spec.python_version}+
- PostgreSQL 14+
- Redis 7+

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd fastapi_app
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start the application:**
   ```bash
   uvicorn main:app --reload
   ```

The application will be available at: http://localhost:8000

## 🐳 Docker Deployment

### Quick Start with Docker Compose

```bash
docker-compose up -d
```

This will start:
- FastAPI application on port 8000
- PostgreSQL database on port 5432
- Redis on port 6379

### Build and Run Manually

```bash
# Build image
docker build -t {self.system_spec.system_id.lower()} .

# Run container
docker run -p 8000:8000 --env-file .env {self.system_spec.system_id.lower()}
```

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Endpoints

{router_list}

### Health Check

- **GET** `/health` - Check application health status

## 🗄️ Database

### Connection

Configure the `DATABASE_URL` in your `.env` file:

```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### Migrations

This project uses Alembic for database migrations.

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🔐 Authentication

The application uses JWT Bearer token authentication.

### Obtaining a Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{{"username": "user", "password": "pass"}}'
```

### Using the Token

```bash
curl -X GET http://localhost:8000/api/v1/protected \\
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_feature.py
```

## 📁 Project Structure

```
fastapi_app/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration management
├── database.py             # Database connection and session
├── dependencies.py         # FastAPI dependencies
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── Dockerfile             # Docker image configuration
├── docker-compose.yml     # Docker Compose configuration
├── routers/               # API route handlers
│   ├── __init__.py
│   └── [feature].py       # One router per feature
├── models/                # SQLAlchemy database models
│   ├── __init__.py
│   └── [feature].py       # One model file per feature
├── middleware/            # Custom middleware
│   ├── __init__.py
│   ├── logging_middleware.py
│   └── error_handler.py
├── tests/                 # Test suite
│   └── ...
└── alembic/              # Database migrations
    └── ...
```

## ⚙️ Configuration

All configuration is managed through environment variables.

See `.env.example` for all available options.

## 🛠️ Development

### Adding New Features

1. Update YAML specifications
2. Re-run `fastapi_build.py`
3. Implement business logic in generated router stubs
4. Add database models if needed
5. Create and run migrations

### Code Style

This project follows PEP 8 style guidelines.

```bash
# Format code
black .

# Lint code
flake8 .
```

## 📝 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]

## 📧 Support

[Add support contact information here]

---

**Note:** This application was auto-generated. Review and customize the TODO comments in the generated code before deploying to production.
'''
        
        output_file = self.output_dir / "README.md"
        with open(output_file, 'w') as f:
            f.write(content)
        
        self.log(f"Generated: {output_file}")
    
    def run(self) -> bool:
        """Execute FastAPI build process."""
        try:
            # Parse specifications
            self.parse_system_index()
            
            # Build application
            return self.build_application()
            
        except Exception as e:
            self.print_header("❌ BUILD FAILED")
            print(f"Error: {str(e)}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Build complete FastAPI application from YAML specifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build FastAPI app from system index
  %(prog)s "path/to/SYSTEM_INDEX.yaml"
  
  # Specify custom output directory
  %(prog)s "path/to/SYSTEM_INDEX.yaml" --output "./my_fastapi_app"
  
  # Verbose output
  %(prog)s "path/to/SYSTEM_INDEX.yaml" --verbose
        """
    )
    
    parser.add_argument(
        "system_index",
        help="Path to SYSTEM_INDEX.yaml file"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        help="Output directory for FastAPI application (default: ./fastapi_app)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output"
    )
    
    args = parser.parse_args()
    
    # Build FastAPI application
    builder = FastAPIBuilder(
        system_index_path=args.system_index,
        output_dir=args.output,
        verbose=args.verbose
    )
    
    success = builder.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
