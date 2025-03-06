# Claude Debug Layer

The Debug Layer is a component of the Claude Optimization Layer that tracks common issues, their solutions, and debugging strategies. This helps Claude provide faster and more accurate assistance when debugging issues in the Atlantis Go codebase.

## Purpose

The Debug Layer serves several important purposes:

1. **Knowledge Preservation**: Documenting debugging sessions and their solutions preserves knowledge that would otherwise be lost
2. **Pattern Recognition**: Identifying common error patterns helps detect similar issues in the future
3. **Solution Acceleration**: Providing ready-made solutions for previously encountered issues
4. **Root Cause Analysis**: Documenting the root causes of bugs helps prevent similar issues in the future
5. **Learning Resource**: Serving as a learning resource for new developers

## Directory Structure

The debug layer is organized as follows:

```
.claude/debug/
  ├── README.md                 # This file
  ├── common_issues.md          # Catalog of frequently encountered issues
  ├── troubleshooting.md        # General troubleshooting strategies
  ├── component/                # Component-specific debugging
  │   ├── core_user_system.md   # Core User System debugging
  │   ├── experience_system.md  # Experience System debugging
  │   ├── zone_system.md        # Zone System debugging
  │   └── economic_system.md    # Economic System debugging
  └── patterns/                 # Pattern-specific debugging
      ├── matrix_flow.md        # Matrix Flow pattern debugging
      ├── virtue_metrics.md     # Virtue Metrics calculations debugging
      ├── experience_prog.md    # Experience Progression debugging
      └── zone_geo.md           # Zone Geographic patterns debugging
```

## Debug Entry Format

Each debug entry should follow this format:

```markdown
## Issue: [Brief description of the issue]

### Symptoms

- Symptom 1: [Description]
- Symptom 2: [Description]
- Error messages: [Exact error messages]

### Affected Components

- [Component 1]
- [Component 2]

### Root Cause

[Detailed explanation of the root cause]

### Solution

[Step-by-step solution including code examples]

### Prevention

[How to prevent this issue in the future]

### Related Issues

- [Link to related issues]
```

## Adding a New Debug Entry

To add a new debug entry, follow these steps:

1. Identify the appropriate file based on the component or pattern affected
2. Add a new entry using the format above
3. Use clear, concise language focusing on the technical details
4. Include code examples where appropriate
5. Add tags for searchability

## Example Debug Entry

Here's an example debug entry:

```markdown
## Issue: VirtueMetrics calculation timeout during high traffic

### Symptoms

- Timeout errors in the logs: "Calculation of VirtueMetrics exceeded time limit"
- High CPU usage during peak traffic periods
- Slow response times on the user dashboard

### Affected Components

- CORE_USER_SYSTEM
- VirtueMetricsService

### Root Cause

The virtue metrics calculation was being performed synchronously for each request,
causing performance degradation during high traffic. The calculation involves complex
database queries that become inefficient when run too frequently.

### Solution

Implemented a caching strategy with a time-based invalidation:

```python
class VirtueMetricsService:
    def calculate_metrics(self, user_id):
        cache_key = f"virtue_metrics_{user_id}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
            
        # Perform the expensive calculation
        result = self._perform_calculation(user_id)
        
        # Cache for 30 minutes
        cache.set(cache_key, result, timeout=1800)
        return result
```

Also added a background task to pre-calculate metrics during off-peak hours:

```python
@shared_task
def precalculate_virtue_metrics():
    users = User.objects.filter(is_active=True)
    for user in users:
        VirtueMetricsService().calculate_metrics(user.id)
```

### Prevention

- Add performance tests for virtue metrics calculation
- Implement monitoring for calculation time
- Document the caching strategy in the VirtueMetrics model documentation
```

## Using the Debug Layer

When debugging issues:

1. Check if a similar issue has been documented
2. Follow the solutions provided
3. If the issue is new, document it after solving
4. Tag the issue appropriately for future reference

## Tags

Use these common tags to categorize issues:

- `#performance` - Performance-related issues
- `#security` - Security-related issues
- `#data-integrity` - Data integrity issues
- `#ui` - User interface issues
- `#api` - API-related issues
- `#authentication` - Authentication issues
- `#authorization` - Authorization issues
- `#concurrency` - Concurrency issues
- `#deployment` - Deployment issues

## Linking to Code References

When referencing code, include the file path and line numbers:

```markdown
See [core/services/virtue_metrics_service.py:45-60](../ref/core/services/virtue_metrics_service.py#L45-L60)
```

This helps Claude find the relevant code quickly when assisting with debugging. 