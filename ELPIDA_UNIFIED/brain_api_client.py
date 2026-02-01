"""
Brain API Client - Clean Implementation
Polls Master_Brain API endpoints for external jobs (A1 enforcement)
"""

import logging
import requests
import time
from typing import List, Dict, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BrainAPIClient:
    """HTTP client for Master_Brain API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.is_healthy = False
        self.connected = False  # For compatibility with runtime initialization
        
        # Attempt initial health check
        try:
            self.check_health()
        except Exception:
            pass  # Will retry during polling
        
    def check_health(self) -> bool:
        """Check Brain API health status"""
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=2
            )
            if response.status_code == 200:
                self.is_healthy = True
                self.connected = True
                logger.info("Brain API health check: OK")
                return True
        except requests.RequestException as e:
            logger.warning(f"Brain API health check failed: {e}")
        
        self.is_healthy = False
        self.connected = False
        return False
    
    def get_candidates(self) -> List[Dict]:
        """Get pattern candidates awaiting review"""
        try:
            response = self.session.get(
                f"{self.base_url}/candidates",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                candidates = data.get('candidates', [])
                count = data.get('count', 0)
                if count > 0:
                    logger.info(f"Retrieved {count} candidates from Brain API")
                return candidates
            else:
                logger.warning(f"Failed to get candidates: {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"Error fetching candidates: {e}")
        
        return []
    
    def get_pending_scans(self) -> List[Dict]:
        """
        Get pending gnosis scans from queue
        PHASE 12.2: Now polls /pending-scans which POPs from async queue
        """
        try:
            response = self.session.get(
                f"{self.base_url}/pending-scans",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                scans = data.get('jobs', [])
                count = data.get('count', 0)
                if count > 0:
                    logger.info(f"Retrieved {count} pending scans from Brain API queue")
                return scans
            else:
                logger.warning(f"Failed to get scans: {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"Error fetching scans: {e}")
        
        return []
    
    def analyze_swarm(self) -> Optional[Dict]:
        """Request swarm consensus/divergence analysis"""
        try:
            response = self.session.post(
                f"{self.base_url}/analyze-swarm",
                json={"request_time": datetime.utcnow().isoformat()},
                timeout=10
            )
            if response.status_code == 200:
                analysis = response.json()
                logger.info("Swarm analysis queued successfully")
                return analysis
            else:
                logger.warning(f"Swarm analysis failed: {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"Error requesting swarm analysis: {e}")
        
        return None


class BrainJobPoller:
    """Polls Brain API and converts responses to prioritized tasks"""
    
    def __init__(self, client: BrainAPIClient):
        self.client = client
        self.intervals = {
            "health": 60,      # Every 60 seconds
            "candidates": 120,  # Every 2 minutes
            "scans": 5,        # Every cycle
            "swarm": 300       # Every 5 minutes
        }
        self.last_checks = {
            "health": 0,
            "candidates": 0,
            "scans": 0,
            "swarm": 0
        }
        self.processed_candidates = set()
        self.processed_scans = set()
    
    def poll(self, current_time: float) -> List[Dict]:
        """
        Poll Brain API endpoints and return prioritized tasks
        
        Returns:
            List of task dicts: {'type': str, 'priority': int, 'payload': dict}
        """
        tasks = []
        
        # Health check (highest priority)
        if current_time - self.last_checks["health"] >= self.intervals["health"]:
            self.last_checks["health"] = current_time
            healthy = self.client.check_health()
            
            if not healthy:
                # Critical: Brain API unhealthy
                tasks.append({
                    'type': 'EVALUATE_STAGNATION',
                    'priority': 10,
                    'payload': {
                        'id': f'BRAIN_HEALTH_CHECK_{int(current_time)}',
                        'source': 'brain_api',
                        'content': 'Brain API health check failed - investigating connectivity',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                })
                # Skip other polls if unhealthy
                return tasks
        
        # Skip polls if Brain not healthy
        if not self.client.is_healthy:
            return tasks
        
        # Pending scans (high priority - epistemic work)
        # PHASE 12.2: Now receives jobs directly from queue
        if current_time - self.last_checks["scans"] >= self.intervals["scans"]:
            self.last_checks["scans"] = current_time
            queued_jobs = self.client.get_pending_scans()
            
            # Process jobs from queue (already have full job structure)
            for job in queued_jobs:
                job_id = job.get('id')
                job_type = job.get('type', 'GNOSIS_SCAN_REQUEST')
                payload = job.get('payload', {})
                priority = job.get('priority', 9)
                
                if job_id and job_id not in self.processed_scans:
                    self.processed_scans.add(job_id)
                    
                    # Map job type to task type
                    task_type_map = {
                        'GNOSIS_SCAN_REQUEST': 'ANALYZE_EXTERNAL_OBJECT',
                        'SWARM_ANALYSIS': 'SYNTHESIZE_PATTERN'
                    }
                    task_type = task_type_map.get(job_type, 'ANALYZE_EXTERNAL_OBJECT')
                    
                    tasks.append({
                        'type': task_type,
                        'priority': priority,
                        'payload': {
                            'id': job_id,
                            'source': payload.get('source', 'brain_api_queue'),
                            'content': payload.get('input_text', str(payload)),
                            'metadata': payload,
                            'timestamp': job.get('timestamp', datetime.utcnow().isoformat())
                        }
                    })
        
        # Pattern candidates (medium priority - governance work)
        if current_time - self.last_checks["candidates"] >= self.intervals["candidates"]:
            self.last_checks["candidates"] = current_time
            candidates = self.client.get_candidates()
            
            for candidate in candidates:
                candidate_id = candidate.get('id') or candidate.get('hash')
                if candidate_id and candidate_id not in self.processed_candidates:
                    self.processed_candidates.add(candidate_id)
                    tasks.append({
                        'type': 'ANALYZE_INSIGHT',
                        'priority': 8,
                        'payload': {
                            'id': f'CANDIDATE_REVIEW_{candidate_id}',
                            'source': 'brain_api_candidate',
                            'content': candidate.get('pattern', str(candidate)),
                            'metadata': candidate,
                            'timestamp': datetime.utcnow().isoformat()
                        }
                    })
        
        # Swarm analysis (lower priority - consensus check)
        if current_time - self.last_checks["swarm"] >= self.intervals["swarm"]:
            self.last_checks["swarm"] = current_time
            swarm_result = self.client.analyze_swarm()
            
            if swarm_result:
                tasks.append({
                    'type': 'SYNTHESIZE_PATTERN',
                    'priority': 7,
                    'payload': {
                        'id': f'SWARM_CONSENSUS_{int(current_time)}',
                        'source': 'brain_api_swarm',
                        'content': str(swarm_result),
                        'metadata': swarm_result,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                })
        
        return tasks
