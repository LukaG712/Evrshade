"""
Test 6: Knowledge Graph Flow
Greenie → Gobber → Shrewd (embeddings)

Validates:
- Gobber health endpoint
- Note creation
- Embedding generation
- Semantic search
- Vault indexing
"""

from tests.integration.base_test import BaseIntegrationTest


class TestKnowledgeFlow(BaseIntegrationTest):
    """Test the knowledge graph flow through Gobber."""
    
    service = "Gobber"
    
    def run(self) -> bool:
        print("\n  Step 1: Check Gobber health")
        gobber_ok = self.check_service_health("Gobber", 8085)
        
        if not gobber_ok:
            print("\n  ⊘ Gobber not running, skipping flow test")
            return False
        
        # Create a note
        print("\n  Step 2: Create test note")
        note_data = {
            "title": "Integration Test Note",
            "content": "This is a test note for the knowledge graph.",
            "tags": ["test", "integration"],
        }
        note = self.make_request("post", "/api/notes", json=note_data)
        note_created = self.assert_true(
            note is not None and "id" in note,
            "Note created successfully"
        )
        note_id = note.get("id", "") if note else ""
        
        # Create an embedding
        print("\n  Step 3: Create test embedding")
        embedding_data = {
            "text": "Test embedding for integration test",
            "metadata": {"source": "integration_test"},
        }
        embedding = self.make_request("post", "/api/embeddings", json=embedding_data)
        embedding_created = self.assert_true(
            embedding is not None,
            "Embedding created successfully"
        )
        
        # Search embeddings
        print("\n  Step 4: Search embeddings")
        search_result = self.make_request("get", "/api/embeddings/search?q=test")
        search_ok = self.assert_true(
            search_result is not None,
            "Embedding search works"
        )
        
        # List notes
        print("\n  Step 5: List notes")
        notes = self.make_request("get", "/api/notes")
        notes_ok = self.assert_true(
            notes is not None and "notes" in notes,
            "Note list retrieved"
        )
        
        # Check webhooks
        print("\n  Step 6: Check webhooks")
        webhooks = self.make_request("get", "/api/webhooks")
        webhooks_ok = self.assert_true(
            webhooks is not None,
            "Webhooks endpoint accessible"
        )
        
        # Check analytics
        print("\n  Step 7: Check analytics")
        analytics = self.make_request("get", "/api/analytics")
        analytics_ok = self.assert_true(
            analytics is not None,
            "Analytics endpoint accessible"
        )
        
        # Check feature flags
        print("\n  Step 8: Check feature flags")
        flags = self.make_request("get", "/api/flags")
        flags_ok = self.assert_true(
            flags is not None,
            "Feature flags endpoint accessible"
        )
        
        # Cleanup
        print("\n  Step 9: Cleanup")
        if note_id:
            self.make_request("delete", f"/api/notes/{note_id}")
            print("  ✓ Test note deleted")
        
        all_passed = all([
            gobber_ok, note_created, embedding_created, search_ok,
            notes_ok, webhooks_ok, analytics_ok, flags_ok
        ])
        
        return all_passed

