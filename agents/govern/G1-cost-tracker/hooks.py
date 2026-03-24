"""G1-cost-tracker specific hooks.

Extends BaseHooks with cost-specific behavior:
- Budget check before invocation
- Cost recording after invocation
"""
from sdk.base_hooks import BaseHooks


class G1Hooks(BaseHooks):
    """Cost-tracker specific hooks. Uses default BaseHooks for now."""
    pass
