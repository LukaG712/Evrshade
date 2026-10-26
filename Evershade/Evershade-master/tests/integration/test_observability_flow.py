"""
Test 5: Observability Flow
All services → Sneaker → Prometheus → Grafana

Validates:
- Sneaker health endpoint
- OTLP trace ingestion
- OTLP log ingestion
- OTLP metric ingestion
- Query endpoints
- Alert rules
"""

from tests.integration.base_test import BaseIntegrationTest


class TestObservabilityFlow(BaseIntegrationTest):
    """Test the observability flow through Sneaker."""
    
    service = "Sneaker"
    
    def run(self) -> bool:
        print("\n  Step 1: Check Sneaker health")
        sneaker_ok = self.check_service_health("Sneaker", 8086)
        
        if not sneaker_ok:
            print("\n  ⊘ Sneaker not running, skipping flow test")
            return False
        
        # Ingest a trace
        print("\n  Step 2: Ingest test trace")
        trace_data = {
            "resource_spans": [{
                "resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "test"}}]},
                "scope_spans": [{
                    "spans": [{
                        "trace_id": "0102030405060708090a0b0c0d0e0f10",
                        "span_id": "0102030405060708",
                        "name": "test.span",
                        "kind": 2,
                    }]
                }]
            }]
        }
        trace_result = self.make_request("post", "/v1/traces", json=trace_data)
        trace_ingested = self.assert_true(
            trace_result is not None,
            "Trace ingested successfully"
        )
        
        # Ingest a log
        print("\n  Step 3: Ingest test log")
        log_data = {
            "resource_logs": [{
                "resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "test"}}]},
                "scope_logs": [{
                    "logs": [{
                        "time_unix_nano": 1700000000000000000,
                        "body": {"stringValue": "Test log message"},
                        "severity_number": 9,
                    }]
                }]
            }]
        }
        log_result = self.make_request("post", "/v1/logs", json=log_data)
        log_ingested = self.assert_true(
            log_result is not None,
            "Log ingested successfully"
        )
        
        # Ingest a metric
        print("\n  Step 4: Ingest test metric")
        metric_data = {
            "resource_metrics": [{
                "resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "test"}}]},
                "scope_metrics": [{
                    "metrics": [{
                        "name": "test_counter",
                        "sum": {
                            "data_points": [{
                                "as_double_value": 1.0,
                                "time_unix_nano": 1700000000000000000,
                            }]
                        }
                    }]
                }]
            }]
        }
        metric_result = self.make_request("post", "/v1/metrics", json=metric_data)
        metric_ingested = self.assert_true(
            metric_result is not None,
            "Metric ingested successfully"
        )
        
        # Query traces
        print("\n  Step 5: Query traces")
        traces = self.make_request("get", "/api/traces")
        traces_ok = self.assert_true(
            traces is not None,
            "Trace query endpoint accessible"
        )
        
        # Query logs
        print("\n  Step 6: Query logs")
        logs = self.make_request("get", "/api/logs")
        logs_ok = self.assert_true(
            logs is not None,
            "Log query endpoint accessible"
        )
        
        # Query metrics
        print("\n  Step 7: Query metrics")
        metrics = self.make_request("get", "/api/metrics")
        metrics_ok = self.assert_true(
            metrics is not None,
            "Metric query endpoint accessible"
        )
        
        # Create alert rule
        print("\n  Step 8: Create alert rule")
        alert_data = {
            "name": "test_alert",
            "metric": "error_rate",
            "condition": ">",
            "threshold": 0.5,
            "window_seconds": 300,
        }
        alert = self.make_request("post", "/api/alerts/rules", json=alert_data)
        alert_created = self.assert_true(
            alert is not None,
            "Alert rule created successfully"
        )
        
        # Check metrics endpoint
        print("\n  Step 9: Check /metrics endpoint")
        prom_metrics = self.make_request("get", "/metrics")
        metrics_endpoint_ok = self.assert_true(
            prom_metrics is not None,
            "Prometheus /metrics endpoint accessible"
        )
        
        all_passed = all([
            sneaker_ok, trace_ingested, log_ingested, metric_ingested,
            traces_ok, logs_ok, metrics_ok, alert_created, metrics_endpoint_ok
        ])
        
        return all_passed

