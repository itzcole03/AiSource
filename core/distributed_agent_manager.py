"""
Distributed Agent Manager - Enables agent execution across multiple nodes
"""

import asyncio
import json
import logging
import aiohttp
from typing import Dict, List, Optional, Set
from datetime import datetime
import hashlib
import socket

class DistributedAgentManager:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger("DistributedAgentManager")
        
        # Node management
        self.node_id = self.generate_node_id()
        self.nodes: Dict[str, Dict] = {}
        self.local_agents: Set[str] = set()
        
        # Load balancing
        self.task_distribution = {}
        self.node_health = {}
        
        # Communication
        self.communication_port = config.get('communication_port', 8900)
        self.discovery_port = config.get('discovery_port', 8901)
        
        # Clustering
        self.cluster_name = config.get('cluster_name', 'ultimate-copilot-cluster')
        self.is_coordinator = False
        self.coordinator_node = None
        
    def generate_node_id(self) -> str:
        """Generate unique node ID"""
        hostname = socket.gethostname()
        timestamp = str(datetime.now().timestamp())
        return hashlib.md5(f"{hostname}_{timestamp}".encode()).hexdigest()[:8]
    
    async def initialize(self):
        """Initialize distributed agent manager"""
        self.logger.info(f"🌐 Initializing Distributed Agent Manager (Node: {self.node_id})...")
        
        # Start communication server
        await self.start_communication_server()
        
        # Start node discovery
        await self.start_node_discovery()
        
        # Join cluster
        await self.join_cluster()
        
        self.logger.info(f"✅ Distributed Agent Manager initialized")
    
    async def start_communication_server(self):
        """Start communication server for inter-node communication"""
        from aiohttp import web
        
        app = web.Application()
        
        # Routes for inter-node communication
        app.router.add_post('/api/task', self.handle_remote_task)
        app.router.add_get('/api/status', self.handle_status_request)
        app.router.add_post('/api/join', self.handle_join_request)
        app.router.add_post('/api/heartbeat', self.handle_heartbeat)
        app.router.add_get('/api/agents', self.handle_agents_request)
        
        # Start server
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, 'localhost', self.communication_port)
        await site.start()
        
        self.logger.info(f"Communication server started on port {self.communication_port}")
    
    async def start_node_discovery(self):
        """Start node discovery service"""
        # Start UDP discovery server
        asyncio.create_task(self.discovery_server())
        
        # Start periodic discovery broadcast
        asyncio.create_task(self.discovery_broadcast())
    
    async def discovery_server(self):
        """UDP server for node discovery"""
        import socket
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', self.discovery_port))
        sock.setblocking(False)
        
        while True:
            try:
                data, addr = await asyncio.get_event_loop().sock_recvfrom(sock, 1024)
                message = json.loads(data.decode())
                
                if message.get('type') == 'discovery' and message.get('cluster') == self.cluster_name:
                    await self.handle_discovery_message(message, addr)
                    
            except Exception as e:
                self.logger.debug(f"Discovery server error: {e}")
                await asyncio.sleep(1)
    
    async def discovery_broadcast(self):
        """Broadcast discovery messages"""
        import socket
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        while True:
            try:
                message = {
                    'type': 'discovery',
                    'cluster': self.cluster_name,
                    'node_id': self.node_id,
                    'communication_port': self.communication_port,
                    'agents': list(self.local_agents),
                    'timestamp': datetime.now().isoformat()
                }
                
                data = json.dumps(message).encode()
                sock.sendto(data, ('<broadcast>', self.discovery_port))
                
                await asyncio.sleep(30)  # Broadcast every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Discovery broadcast error: {e}")
                await asyncio.sleep(60)
    
    async def handle_discovery_message(self, message: Dict, addr):
        """Handle discovery message from another node"""
        node_id = message.get('node_id')
        
        if node_id != self.node_id:  # Ignore own messages
            node_info = {
                'node_id': node_id,
                'address': addr[0],
                'communication_port': message.get('communication_port'),
                'agents': message.get('agents', []),
                'last_seen': datetime.now().isoformat(),
                'status': 'active'
            }
            
            self.nodes[node_id] = node_info
            self.logger.info(f"Discovered node: {node_id} at {addr[0]}")
    
    async def join_cluster(self):
        """Join the cluster and elect coordinator"""
        await asyncio.sleep(5)  # Wait for initial discovery
        
        if not self.nodes:
            # First node becomes coordinator
            self.is_coordinator = True
            self.coordinator_node = self.node_id
            self.logger.info(f"🎯 Node {self.node_id} elected as cluster coordinator")
        else:
            # Find coordinator or elect new one
            await self.elect_coordinator()
    
    async def elect_coordinator(self):
        """Elect cluster coordinator"""
        # Simple election: node with smallest ID becomes coordinator
        all_nodes = [self.node_id] + list(self.nodes.keys())
        coordinator = min(all_nodes)
        
        if coordinator == self.node_id:
            self.is_coordinator = True
            self.coordinator_node = self.node_id
            self.logger.info(f"🎯 Node {self.node_id} elected as cluster coordinator")
        else:
            self.coordinator_node = coordinator
            self.logger.info(f"📡 Node {coordinator} is cluster coordinator")
    
    async def register_local_agent(self, agent_id: str):
        """Register an agent as running on this node"""
        self.local_agents.add(agent_id)
        self.logger.info(f"📝 Registered local agent: {agent_id}")
    
    async def unregister_local_agent(self, agent_id: str):
        """Unregister a local agent"""
        self.local_agents.discard(agent_id)
        self.logger.info(f"🗑️ Unregistered local agent: {agent_id}")
    
    async def execute_distributed_task(self, task: Dict) -> Dict:
        """Execute task on optimal node"""
        # Determine best node for task
        target_node = await self.select_optimal_node(task)
        
        if target_node == self.node_id:
            # Execute locally
            return await self.execute_local_task(task)
        else:
            # Execute remotely
            return await self.execute_remote_task(task, target_node)
    
    async def select_optimal_node(self, task: Dict) -> str:
        """Select optimal node for task execution"""
        required_agent = task.get('agent', 'orchestrator')
        
        # Find nodes with the required agent
        candidate_nodes = []
        
        # Check local node
        if required_agent in self.local_agents:
            candidate_nodes.append({
                'node_id': self.node_id,
                'load': len(self.task_distribution.get(self.node_id, [])),
                'local': True
            })
        
        # Check remote nodes
        for node_id, node_info in self.nodes.items():
            if required_agent in node_info.get('agents', []):
                candidate_nodes.append({
                    'node_id': node_id,
                    'load': len(self.task_distribution.get(node_id, [])),
                    'local': False
                })
        
        if not candidate_nodes:
            # No specific agent found, use any available node
            candidate_nodes = [{'node_id': self.node_id, 'load': 0, 'local': True}]
            for node_id in self.nodes.keys():
                candidate_nodes.append({
                    'node_id': node_id,
                    'load': len(self.task_distribution.get(node_id, [])),
                    'local': False
                })
        
        # Select node with lowest load, prefer local
        best_node = min(candidate_nodes, key=lambda x: (x['load'], not x['local']))
        
        return best_node['node_id']
    
    async def execute_local_task(self, task: Dict) -> Dict:
        """Execute task locally"""
        # This would integrate with the local agent manager
        # For now, return a placeholder result
        
        return {
            'success': True,
            'node_id': self.node_id,
            'execution_type': 'local',
            'result': 'Task executed locally',
            'timestamp': datetime.now().isoformat()
        }
    
    async def execute_remote_task(self, task: Dict, target_node: str) -> Dict:
        """Execute task on remote node"""
        if target_node not in self.nodes:
            raise Exception(f"Target node {target_node} not available")
        
        node_info = self.nodes[target_node]
        url = f"http://{node_info['address']}:{node_info['communication_port']}/api/task"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=task) as response:
                    if response.status == 200:
                        result = await response.json()
                        result['execution_type'] = 'remote'
                        result['target_node'] = target_node
                        return result
                    else:
                        raise Exception(f"Remote execution failed: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Remote task execution failed: {e}")
            # Fallback to local execution
            return await self.execute_local_task(task)
    
    async def handle_remote_task(self, request):
        """Handle remote task execution request"""
        try:
            task = await request.json()
            result = await self.execute_local_task(task)
            
            return aiohttp.web.json_response(result)
            
        except Exception as e:
            return aiohttp.web.json_response(
                {'success': False, 'error': str(e)}, 
                status=500
            )
    
    async def handle_status_request(self, request):
        """Handle status request from other nodes"""
        status = {
            'node_id': self.node_id,
            'agents': list(self.local_agents),
            'load': len(self.task_distribution.get(self.node_id, [])),
            'is_coordinator': self.is_coordinator,
            'timestamp': datetime.now().isoformat()
        }
        
        return aiohttp.web.json_response(status)
    
    async def handle_join_request(self, request):
        """Handle join request from new node"""
        try:
            node_info = await request.json()
            node_id = node_info.get('node_id')
            
            if node_id and node_id != self.node_id:
                self.nodes[node_id] = {
                    **node_info,
                    'last_seen': datetime.now().isoformat(),
                    'status': 'active'
                }
                
                self.logger.info(f"Node {node_id} joined cluster")
            
            return aiohttp.web.json_response({'success': True})
            
        except Exception as e:
            return aiohttp.web.json_response(
                {'success': False, 'error': str(e)}, 
                status=400
            )
    
    async def handle_heartbeat(self, request):
        """Handle heartbeat from other nodes"""
        try:
            heartbeat = await request.json()
            node_id = heartbeat.get('node_id')
            
            if node_id in self.nodes:
                self.nodes[node_id]['last_seen'] = datetime.now().isoformat()
                self.nodes[node_id]['status'] = 'active'
            
            return aiohttp.web.json_response({'success': True})
            
        except Exception as e:
            return aiohttp.web.json_response(
                {'success': False, 'error': str(e)}, 
                status=400
            )
    
    async def handle_agents_request(self, request):
        """Handle request for available agents"""
        agents_info = {}
        
        # Local agents
        agents_info[self.node_id] = list(self.local_agents)
        
        # Remote agents
        for node_id, node_info in self.nodes.items():
            agents_info[node_id] = node_info.get('agents', [])
        
        return aiohttp.web.json_response(agents_info)
    
    async def monitor_cluster_health(self):
        """Monitor cluster health and handle node failures"""
        while True:
            try:
                current_time = datetime.now()
                failed_nodes = []
                
                for node_id, node_info in self.nodes.items():
                    last_seen = datetime.fromisoformat(node_info.get('last_seen', ''))
                    
                    if (current_time - last_seen).seconds > 120:  # 2 minutes timeout
                        failed_nodes.append(node_id)
                        self.logger.warning(f"Node {node_id} appears to be offline")
                
                # Remove failed nodes
                for node_id in failed_nodes:
                    del self.nodes[node_id]
                    
                    # Redistribute tasks if necessary
                    if node_id in self.task_distribution:
                        await self.redistribute_tasks(node_id)
                
                # Re-elect coordinator if needed
                if self.coordinator_node in failed_nodes:
                    await self.elect_coordinator()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Cluster health monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def redistribute_tasks(self, failed_node: str):
        """Redistribute tasks from failed node"""
        if failed_node not in self.task_distribution:
            return
        
        failed_tasks = self.task_distribution[failed_node]
        del self.task_distribution[failed_node]
        
        # Redistribute to other nodes
        for task in failed_tasks:
            optimal_node = await self.select_optimal_node(task)
            
            if optimal_node not in self.task_distribution:
                self.task_distribution[optimal_node] = []
            
            self.task_distribution[optimal_node].append(task)
        
        self.logger.info(f"Redistributed {len(failed_tasks)} tasks from failed node {failed_node}")
    
    def get_cluster_status(self) -> Dict:
        """Get cluster status"""
        return {
            'node_id': self.node_id,
            'is_coordinator': self.is_coordinator,
            'coordinator_node': self.coordinator_node,
            'cluster_name': self.cluster_name,
            'total_nodes': len(self.nodes) + 1,  # +1 for self
            'local_agents': list(self.local_agents),
            'nodes': {
                node_id: {
                    'agents': node_info.get('agents', []),
                    'status': node_info.get('status', 'unknown'),
                    'last_seen': node_info.get('last_seen')
                }
                for node_id, node_info in self.nodes.items()
            }
        }
    
    async def stop(self):
        """Stop distributed agent manager"""
        self.logger.info("🛑 Stopping Distributed Agent Manager...")
        
        # Notify other nodes of departure
        await self.broadcast_departure()
        
        # Stop services
        # (Server cleanup would be handled by the framework)
    
    async def shutdown(self):
        """Shutdown distributed agent manager"""
        self.logger.info("Distributed Agent Manager shutdown complete")
        # Clean up node connections and resources
        self.nodes.clear()
        self.local_agents.clear()

    async def broadcast_departure(self):
        """Broadcast departure message to cluster"""
        departure_message = {
            'type': 'departure',
            'node_id': self.node_id,
            'timestamp': datetime.now().isoformat()
        }
        
        for node_id, node_info in self.nodes.items():
            try:
                url = f"http://{node_info['address']}:{node_info['communication_port']}/api/departure"
                
                async with aiohttp.ClientSession() as session:
                    await session.post(url, json=departure_message)
                    
            except Exception as e:
                self.logger.debug(f"Failed to notify node {node_id} of departure: {e}")