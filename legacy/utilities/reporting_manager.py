#!/usr/bin/env python3
"""
Control Tower Reporting Manager
Manages timestamped reports and tracks query history for easy reuse
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import hashlib

class ReportingManager:
    """
    Manages Control Tower reports and query tracking
    """
    
    def __init__(self):
        """Initialize the reporting manager"""
        self.reporting_dir = "/workspaces/control_tower/reporting"
        self.queries_file = os.path.join(self.reporting_dir, "control_tower_queries.json")
        self.commands_file = os.path.join(self.reporting_dir, "control_tower_commands.md")
        
        # Ensure reporting directory exists
        os.makedirs(self.reporting_dir, exist_ok=True)
        
        # Load existing queries
        self.query_history = self._load_query_history()
    
    def _load_query_history(self) -> Dict:
        """Load the query history from file"""
        try:
            if os.path.exists(self.queries_file):
                with open(self.queries_file, 'r') as f:
                    return json.load(f)
            return {"queries": [], "last_updated": datetime.now().isoformat()}
        except Exception as e:
            print(f"⚠️  Warning: Could not load query history: {e}")
            return {"queries": [], "last_updated": datetime.now().isoformat()}
    
    def _save_query_history(self):
        """Save the query history to file"""
        try:
            self.query_history["last_updated"] = datetime.now().isoformat()
            with open(self.queries_file, 'w') as f:
                json.dump(self.query_history, f, indent=2)
        except Exception as e:
            print(f"⚠️  Warning: Could not save query history: {e}")
    
    def _generate_query_hash(self, query_type: str, parameters: Dict) -> str:
        """Generate a unique hash for a query to detect duplicates"""
        query_string = f"{query_type}_{json.dumps(parameters, sort_keys=True)}"
        return hashlib.md5(query_string.encode()).hexdigest()[:8]
    
    def _is_new_query(self, query_hash: str) -> bool:
        """Check if this is a new query we haven't seen before"""
        existing_hashes = [q.get("hash", "") for q in self.query_history["queries"]]
        return query_hash not in existing_hashes
    
    def _generate_timestamp(self) -> str:
        """Generate timestamp for file naming"""
        return datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def _generate_readable_timestamp(self) -> str:
        """Generate human-readable timestamp for reports"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def track_query(self, query_type: str, command: str, parameters: Dict = None) -> tuple[str, bool]:
        """
        Track a query and determine if it's new
        
        Args:
            query_type: Type of query (e.g., 'status', 'milestones', 'overdue')
            command: Full command to execute
            parameters: Query parameters for deduplication
            
        Returns:
            tuple: (query_hash, is_new_query)
        """
        if parameters is None:
            parameters = {}
            
        query_hash = self._generate_query_hash(query_type, parameters)
        is_new = self._is_new_query(query_hash)
        
        if is_new:
            # Add to query history
            query_entry = {
                "hash": query_hash,
                "type": query_type,
                "command": command,
                "parameters": parameters,
                "first_run": self._generate_readable_timestamp(),
                "run_count": 1
            }
            self.query_history["queries"].append(query_entry)
            self._save_query_history()
            self._update_commands_file()
        else:
            # Update run count for existing query
            for query in self.query_history["queries"]:
                if query.get("hash") == query_hash:
                    query["run_count"] = query.get("run_count", 1) + 1
                    query["last_run"] = self._generate_readable_timestamp()
                    break
            self._save_query_history()
        
        return query_hash, is_new
    
    def _update_commands_file(self):
        """Update the markdown file with all available commands"""
        try:
            content = []
            content.append("# Control Tower Queries\n")
            content.append(f"**Last Updated**: {self._generate_readable_timestamp()}\n")
            content.append("Copy and paste these commands to quickly rerun reports:\n\n")
            
            # Group queries by type
            query_types = {}
            for query in self.query_history["queries"]:
                qtype = query["type"]
                if qtype not in query_types:
                    query_types[qtype] = []
                query_types[qtype].append(query)
            
            # Generate sections for each query type
            for qtype, queries in sorted(query_types.items()):
                content.append(f"## {qtype.title()} Queries\n")
                
                for query in queries:
                    run_info = f"*First run: {query['first_run']} | Run count: {query.get('run_count', 1)}*"
                    content.append(f"### {query['type']} Report")
                    content.append(f"{run_info}\n")
                    content.append("```bash")
                    content.append(query['command'])
                    content.append("```\n")
            
            # Write to file
            with open(self.commands_file, 'w') as f:
                f.write('\n'.join(content))
                
        except Exception as e:
            print(f"⚠️  Warning: Could not update commands file: {e}")
    
    def save_report(self, report_name: str, report_content: str, query_hash: str = None) -> str:
        """
        Save a timestamped report
        
        Args:
            report_name: Name of the report (e.g., 'project_status', 'milestones')
            report_content: Content of the report
            query_hash: Optional hash to link report to query
            
        Returns:
            str: Path to saved report file
        """
        timestamp = self._generate_timestamp()
        filename = f"{timestamp}_{report_name}.md"
        filepath = os.path.join(self.reporting_dir, filename)
        
        # Prepare report with header
        full_content = []
        full_content.append(f"# {report_name.replace('_', ' ').title()} Report")
        full_content.append(f"**Generated**: {self._generate_readable_timestamp()}")
        if query_hash:
            full_content.append(f"**Query Hash**: {query_hash}")
        full_content.append(f"**Source**: Control Tower MS Project Integration\n")
        full_content.append("---\n")
        full_content.append(report_content)
        
        try:
            with open(filepath, 'w') as f:
                f.write('\n'.join(full_content))
            
            print(f"📄 Report saved: {filename}")
            return filepath
            
        except Exception as e:
            print(f"❌ Failed to save report: {e}")
            return ""
    
    def get_recent_reports(self, report_type: str = None, limit: int = 5) -> List[str]:
        """Get list of recent reports, optionally filtered by type"""
        try:
            files = os.listdir(self.reporting_dir)
            reports = [f for f in files if f.endswith('.md') and f != 'control_tower_commands.md']
            
            if report_type:
                reports = [f for f in reports if report_type in f]
            
            # Sort by timestamp (newest first)
            reports.sort(reverse=True)
            return reports[:limit]
            
        except Exception:
            return []
    
    def show_query_stats(self):
        """Display statistics about query usage"""
        print(f"\n📊 QUERY STATISTICS:")
        print(f"Total unique queries: {len(self.query_history['queries'])}")
        
        # Show most common query types
        type_counts = {}
        for query in self.query_history["queries"]:
            qtype = query["type"]
            count = query.get("run_count", 1)
            type_counts[qtype] = type_counts.get(qtype, 0) + count
        
        print(f"\n🔥 MOST USED QUERIES:")
        for qtype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {qtype}: {count} times")
        
        # Show recent reports
        recent = self.get_recent_reports()
        if recent:
            print(f"\n📄 RECENT REPORTS:")
            for report in recent:
                print(f"  • {report}")
