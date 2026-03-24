"""
Railway GraphQL v2 API client for log retrieval.

Wraps https://backboard.railway.com/graphql/v2 to fetch deploy logs,
build logs, and deployment status across multiple Railway projects.
"""

import logging
import os
import time
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

RAILWAY_API_URL = "https://backboard.railway.com/graphql/v2"
MAX_RETRIES = 3
RETRY_DELAY = 1.0


class RailwayClient:
    """Thin GraphQL client for Railway v2 API."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("RAILWAY_TOKEN", "")
        if not self.token:
            raise ValueError(
                "RAILWAY_TOKEN not set. Pass token= or set the environment variable."
            )

    def _gql(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a GraphQL request with retry logic."""
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                resp = requests.post(
                    RAILWAY_API_URL,
                    json={"query": query, "variables": variables or {}},
                    headers={
                        "Authorization": f"Bearer {self.token}",
                        "Content-Type": "application/json",
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                body = resp.json()
                if "errors" in body:
                    error_msg = body["errors"][0].get("message", str(body["errors"]))
                    raise RuntimeError(f"Railway API error: {error_msg}")
                return body.get("data", {})
            except requests.exceptions.HTTPError as e:
                if resp.status_code == 429:
                    wait = RETRY_DELAY * (2 ** attempt)
                    logger.warning(f"Rate limited, retrying in {wait}s...")
                    time.sleep(wait)
                    last_error = e
                    continue
                raise
            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                raise
        raise RuntimeError(f"Railway API failed after {MAX_RETRIES} retries: {last_error}")

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects visible to the token."""
        data = self._gql("""
            query {
                projects {
                    edges {
                        node {
                            id
                            name
                            services {
                                edges {
                                    node {
                                        id
                                        name
                                    }
                                }
                            }
                            environments {
                                edges {
                                    node {
                                        id
                                        name
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """)
        projects = []
        for edge in data.get("projects", {}).get("edges", []):
            node = edge["node"]
            services = [
                {"id": s["node"]["id"], "name": s["node"]["name"]}
                for s in node.get("services", {}).get("edges", [])
            ]
            environments = [
                {"id": e["node"]["id"], "name": e["node"]["name"]}
                for e in node.get("environments", {}).get("edges", [])
            ]
            projects.append({
                "id": node["id"],
                "name": node["name"],
                "services": services,
                "environments": environments,
            })
        return projects

    # ------------------------------------------------------------------
    # Deployments
    # ------------------------------------------------------------------

    def list_deployments(
        self, service_id: str, environment_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """List recent deployments for a service+environment."""
        data = self._gql(
            """
            query($input: DeploymentListInput!, $first: Int) {
                deployments(
                    input: $input
                    first: $first
                ) {
                    edges {
                        node {
                            id
                            status
                            createdAt
                        }
                    }
                }
            }
            """,
            {
                "input": {
                    "serviceId": service_id,
                    "environmentId": environment_id,
                },
                "first": limit,
            },
        )
        deployments = []
        for edge in data.get("deployments", {}).get("edges", []):
            node = edge["node"]
            meta = node.get("meta") or {}
            deployments.append({
                "id": node["id"],
                "status": node.get("status", "UNKNOWN"),
                "created_at": node.get("createdAt", ""),
                "commit_message": meta.get("commitMessage", ""),
                "commit_hash": meta.get("commitHash", ""),
            })
        return deployments

    def get_latest_deployment_id(
        self, service_id: str, environment_id: str
    ) -> Optional[str]:
        """Get the ID of the most recent deployment."""
        deploys = self.list_deployments(service_id, environment_id, limit=1)
        return deploys[0]["id"] if deploys else None

    # ------------------------------------------------------------------
    # Logs
    # ------------------------------------------------------------------

    def get_deploy_logs(
        self, deployment_id: str, limit: int = 500
    ) -> List[Dict[str, Any]]:
        """Fetch runtime/deploy logs for a deployment."""
        data = self._gql(
            """
            query($deploymentId: String!, $limit: Int) {
                deploymentLogs(deploymentId: $deploymentId, limit: $limit) {
                    message
                    timestamp
                    severity
                }
            }
            """,
            {"deploymentId": deployment_id, "limit": limit},
        )
        return data.get("deploymentLogs", [])

    def get_build_logs(
        self, deployment_id: str, limit: int = 500
    ) -> List[Dict[str, Any]]:
        """Fetch build/compile logs for a deployment."""
        data = self._gql(
            """
            query($deploymentId: String!, $limit: Int) {
                buildLogs(deploymentId: $deploymentId, limit: $limit) {
                    message
                    timestamp
                }
            }
            """,
            {"deploymentId": deployment_id, "limit": limit},
        )
        return data.get("buildLogs", [])
