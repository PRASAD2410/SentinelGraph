"""Optional Neo4j persistence adapter. The app remains usable in demo-memory mode."""
import os
from neo4j import GraphDatabase

class NeoStore:
    def __init__(self):
        self.driver = None
        uri=os.getenv('NEO4J_URI'); password=os.getenv('NEO4J_PASSWORD')
        if uri and password:
            try:
                self.driver=GraphDatabase.driver(uri, auth=(os.getenv('NEO4J_USER','neo4j'),password))
                self.driver.verify_connectivity()
            except Exception:
                self.driver=None
    @property
    def available(self): return self.driver is not None
    def seed(self, nodes, edges):
        if not self.driver: return
        with self.driver.session() as s:
            s.run('CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE')
            for n in nodes.values():
                s.run('MERGE (n:Entity {id:$id}) SET n.label=$label,n.type=$type,n.risk=$risk', **n)
            for e in edges:
                s.run('MATCH (a:Entity {id:$source}),(b:Entity {id:$target}) MERGE (a)-[r:RELATED {kind:$label, reportId:$reportId}]->(b) SET r.provenance=$reportId', **e)
    def add_extraction(self, entities, relationships, report_id):
        if not self.driver: return
        with self.driver.session() as s:
            for n in entities:
                s.run('MERGE (n:Entity {id:$id}) SET n.label=$label,n.type=$type,n.confidence=$confidence', **n)
            for rel in relationships:
                s.run('MATCH (a:Entity {id:$source}),(b:Entity {id:$target}) CREATE (a)-[r:RELATED {kind:$type,reportId:$reportId,confidence:$confidence}]->(b) SET r.provenance=$reportId', **rel, reportId=report_id)
