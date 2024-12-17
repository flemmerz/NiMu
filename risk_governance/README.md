# Risk Governance Framework

Enhanced risk detection and monitoring framework for the NiMu platform.

## Structure

```
/detection
  - shell_company_detector.py     # Base shell company detection
  - uk_shell_detector.py         # UK-specific detection rules
  - network_analyzer.py          # Network analysis tools

/monitoring
  - temporal_monitor.py          # Long-term pattern monitoring
  - behavior_monitor.py          # Behavioral pattern analysis
  - relationship_monitor.py      # Business relationship tracking

/governance
  - risk_policies.md            # Risk governance policies
  - scoring_rules.md            # Risk scoring methodology
  - review_process.md           # Risk review procedures
```