"""
backend/src/core/conversation/
├── __init__.py
├── manager.py                 # Main conversation manager (combines state & journey routing)
├── models.py                  # All data models (ConversationState, Context, Session, etc.)
├── transitions.py             # State transition rules and validation
├── journeys/                  # Customer journey implementations
│   ├── __init__.py
│   ├── base.py               # BaseJourney abstract class
│   ├── product_search/       # Product search journey
│   │   ├── __init__.py
│   │   ├── journey.py        # ProductSearchJourney class
│   │   ├── states.py         # All states for this journey
│   │   └── templates.yaml    # Message templates for this journey
│   ├── order_status/         # Order status journey (future)
│   │   └── ...
│   └── menu/                 # Intent menu (special journey)
│       ├── __init__.py
│       ├── state.py          # IntentMenuState
│       └── templates.yaml
└── utils/                    # Utilities
    ├── __init__.py
    ├── parser.py             # Intent/input parsing
    └── formatter.py          # Message formatting
"""