# docs/PROJECT_OVERVIEW.md
# Path: docs/PROJECT_OVERVIEW.md

# Colombian Aftermarket RAG Chatbot - Project Overview

## Executive Summary

The Colombian Aftermarket RAG Chatbot is an AI-powered conversational system designed to revolutionize the automotive parts aftermarket in Colombia. It provides intelligent, multilingual assistance for brake component searches, technical information, pricing, and order management through both web and WhatsApp interfaces.

## Project Objectives

### Primary Goals
1. **Democratize Access**: Enable small and medium automotive repair shops across Colombia to easily find and order brake components
2. **Bridge Language Barriers**: Provide seamless Spanish/English support for international suppliers and local mechanics
3. **Reduce Friction**: Eliminate the complexity of part number searches through natural conversation
4. **Increase Efficiency**: Automate routine inquiries and order processing

### Business Objectives
- Increase sales conversion by 40% through intelligent product recommendations
- Reduce customer service workload by 60% via automation
- Expand market reach to underserved regions of Colombia
- Build trust through transparent, explainable AI responses

## Target Users

### 1. **Independent Mechanics** (40% of user base)
- Small repair shops in Colombian cities
- Limited technical knowledge of part numbers
- Prefer WhatsApp communication
- Need quick price quotes and availability

### 2. **Retail Customers** (35% of user base)
- Vehicle owners seeking DIY repairs
- Price-sensitive buyers
- Need installation guidance
- Prefer web interface

### 3. **Wholesale Buyers** (25% of user base)
- Auto parts stores
- Fleet maintenance companies
- Bulk order requirements
- Need B2B pricing and credit terms

## System Architecture

### Core Components

#### 1. **Conversational AI Engine**
- **LangChain**: Orchestrates multi-step reasoning
- **RAG (Retrieval Augmented Generation)**: Combines database knowledge with LLM capabilities
- **Intent Classification**: Understands user needs in natural language
- **Context Management**: Maintains conversation state across sessions

#### 2. **Knowledge Base**
- **TecDoc Integration**: Real-time access to comprehensive parts catalog
- **Vector Database**: Semantic search through technical manuals
- **Structured Data**: Inventory, pricing, and compatibility information
- **Unstructured Documents**: Repair guides, specifications, policies

#### 3. **Multi-Channel Interface**
- **Web Application**: Next.js-based responsive interface
- **WhatsApp Business**: Native messaging experience
- **Unified Backend**: Consistent experience across channels

#### 4. **Responsible AI Layer**
- **Infosys RAI Toolkit**: Ensures ethical AI practices
- **Chain of Thought (CoT)**: Transparent reasoning process
- **Bias Detection**: Prevents discriminatory responses
- **Hallucination Prevention**: Validates all technical information

## Key Features

### 1. **Intelligent Product Search**
```
User: "Necesito pastillas de freno para una Mazda 3 2018"
Bot: "He encontrado 3 opciones de pastillas de freno para su Mazda 3 2018:
     1. HELLA 8DB355 - Delanteras - $125,000 COP
     2. ATE 13.0460 - Delanteras - $98,000 COP
     3. BREMBO P23077 - Traseras - $87,000 COP"
```

### 2. **Technical Assistance**
- Torque specifications
- Installation procedures
- Compatibility verification
- Troubleshooting guides

### 3. **Smart Pricing**
- Real-time inventory checks
- Tiered pricing (retail/wholesale)
- Automatic quantity discounts
- Shipping cost calculation

### 4. **Order Management**
- Quote generation
- Order tracking
- Delivery scheduling
- Payment method selection

### 5. **Multilingual Support**
- Seamless Spanish/English switching
- Context-aware translations
- Technical terminology handling

## Technical Stack

### Backend
- **FastAPI**: High-performance Python API framework
- **Supabase**: PostgreSQL + pgvector for semantic search
- **Firebase Auth**: Secure authentication
- **Upstash Redis**: Session management and caching
- **LangChain**: AI orchestration

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Firebase SDK**: Client-side authentication

### AI/ML
- **OpenAI GPT-4**: Natural language understanding
- **Embeddings**: text-embedding-3-small for semantic search
- **Infosys RAI**: Responsible AI safeguards

### Integrations
- **WhatsApp Business API**: Messaging platform
- **TecDoc API**: Automotive parts database
- **Colombian Payment Gateways**: Nequi, Daviplata, PSE

## Use Cases

### Use Case 1: Part Identification via Photo
```
Mechanic sends photo of worn brake pad via WhatsApp
→ System identifies part type
→ Suggests compatible replacements
→ Provides pricing and availability
→ Generates quote
```

### Use Case 2: Technical Specification Lookup
```
User asks about torque specs for brake caliper bolts
→ System searches technical database
→ Provides specific values for vehicle model
→ Includes safety warnings
→ Offers installation guide download
```

### Use Case 3: Bulk Order with Negotiation
```
Wholesale buyer requests quote for 50 brake disc sets
→ System checks stock levels
→ Applies wholesale pricing
→ Calculates volume discounts
→ Provides delivery timeline
→ Enables price negotiation
```

### Use Case 4: Emergency Part Sourcing
```
User needs urgent brake parts outside business hours
→ System identifies critical need
→ Checks nearest warehouse stock
→ Provides emergency contact
→ Arranges expedited delivery
```

## Data Flow

### 1. **User Input Processing**
```
User Message → Language Detection → Intent Classification → Entity Extraction
```

### 2. **Information Retrieval**
```
Query Formulation → TecDoc API Call → Vector Search → SQL Query → Result Aggregation
```

### 3. **Response Generation**
```
Context Building → LLM Prompt → RAI Validation → Response Formatting → Translation
```

### 4. **Session Management**
```
Firebase Auth → Redis Session → Context Storage → Analytics Tracking
```

## Security & Compliance

### Data Protection
- End-to-end encryption for sensitive data
- PII anonymization in logs
- GDPR-compliant data handling
- Colombian data protection law compliance

### Authentication
- Firebase Auth with MFA support
- Role-based access control
- API key management
- Session timeout policies

### AI Safety
- Prompt injection prevention
- Output validation
- Bias monitoring
- Explainable AI traces

## Performance Metrics

### Technical KPIs
- Response time: < 2 seconds
- Accuracy: > 95% for part identification
- Uptime: 99.9% availability
- Concurrent users: 1000+

### Business KPIs
- Conversion rate: 25% from inquiry to order
- Customer satisfaction: > 4.5/5 rating
- Query resolution: 80% without human intervention
- Average order value: 350,000 COP

## Deployment Strategy

### Phase 1: MVP (Months 1-2)
- Basic chat interface
- Core part search
- WhatsApp integration
- 100 pilot users

### Phase 2: Enhancement (Months 3-4)
- Advanced technical features
- Multi-language support
- Analytics dashboard
- 500 active users

### Phase 3: Scale (Months 5-6)
- Full catalog integration
- B2B features
- Mobile app
- 2000+ users

## Future Enhancements

### Short Term (6 months)
- Voice message support
- AR part visualization
- Predictive maintenance alerts
- Loyalty program integration

### Long Term (12+ months)
- Expansion to other vehicle systems
- Integration with repair shop management systems
- AI-powered diagnostics
- Marketplace for used parts

## Success Factors

### Critical Success Factors
1. **Accurate Part Matching**: Must correctly identify parts 95%+ of the time
2. **Local Context**: Deep understanding of Colombian market needs
3. **Trust Building**: Transparent pricing and reliable information
4. **User Experience**: Simple, intuitive interface for non-technical users

### Risk Mitigation
- **Technical Risks**: Redundant systems, comprehensive testing
- **Market Risks**: Pilot program, iterative development
- **Regulatory Risks**: Legal compliance review, data protection measures
- **Operational Risks**: 24/7 monitoring, automated failovers

## Conclusion

The Colombian Aftermarket RAG Chatbot represents a significant advancement in automotive parts distribution, combining cutting-edge AI technology with deep market understanding. By focusing on user needs, maintaining high ethical standards, and leveraging modern cloud infrastructure, this system is positioned to transform how brake components are sourced and sold in Colombia.

The modular architecture ensures scalability, the multi-channel approach maximizes reach, and the responsible AI framework builds trust. With clear objectives, defined success metrics, and a phased implementation plan, this project is ready to deliver substantial value to all stakeholders in the Colombian automotive aftermarket.
