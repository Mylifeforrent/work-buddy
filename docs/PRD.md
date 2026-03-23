# Product Requirements Document (PRD)
# Work Buddy - Multi-Agent SDLC Automation System

**Document Version:** 1.0
**Created:** 2026-03-23
**Author:** User Requirements
**Status:** Draft for Review

---

## 1. Executive Summary

Work Buddy is a multi-agent system designed to automate repetitive, time-consuming tasks throughout the Software Development Life Cycle (SDLC). By leveraging AI agents, browser automation, and integration with enterprise tools (Jira, Confluence, OpenSearch, Grafana), Work Buddy reduces manual overhead and ensures consistency in documentation, testing evidence, and compliance validation.

---

## 2. Problem Statement

### 2.1 Pain Points by SDLC Phase

| Phase | Pain Point | Impact |
|-------|------------|--------|
| **Requirements** | Manual Jira task creation with repetitive field population (Epic, Labels, Sprints, Description templates) | Time-consuming, error-prone, inconsistent formatting |
| **Development** | Test results (Dev, UAT, Regression, Performance) must be manually entered into Jira comments with evidence | Repetitive work, delayed evidence posting |
| **Testing** | Iterative upgrades require repeatedly collecting test evidence; manual screenshot capture for web apps is tedious | Time sink, incomplete evidence coverage |
| **Release Prep** | Manual verification of testing evidence, template compliance, CR/ICE details | Compliance gaps discovered late, release delays |
| **Daily Docs** | Difficulty finding specific articles/specs in Confluence pages | Wasted time searching, outdated information used |
| **PVT** | Fixed health check steps after upstream maintenance are repetitive (login screenshots, keyword checks, log extraction) | Manual repetition, inconsistent execution |
| **Production Support** | Alert triage requires cross-referencing Grafana, Prometheus, OpenSearch logs | Slow response time, inconsistent analysis |

### 2.2 Key Problems Summary

1. **Repetitive Manual Tasks:** Many SDLC tasks follow predictable patterns that could be automated
2. **Evidence Collection Overhead:** Gathering and posting testing evidence is time-consuming
3. **Compliance Validation Burden:** Manual verification is inconsistent and error-prone
4. **Documentation Discovery:** Finding relevant Confluence documentation is difficult
5. **Alert Triage Complexity:** Correlating data across multiple observability tools is slow

---

## 3. Target Users

| User Role | Primary Needs |
|-----------|---------------|
| **Software Engineer** | Create Jira tasks, post test evidence, find documentation |
| **QA Engineer** | Capture test evidence, run browser tests, generate reports |
| **Release Manager** | Verify compliance, prepare release documentation |
| **SRE / Production Support** | Triage alerts, run PVT health checks, analyze logs |
| **Project Manager** | Track compliance status, view evidence summary |

---

## 4. Functional Requirements

### 4.1 Requirements Phase - Jira Task Automation

#### FR-1.1: Automated Jira Task Creation
**Priority:** High | **Status:** Implemented

The system SHALL create Jira tasks from requirement descriptions, auto-populating:
- Epic link
- Sprint assignment
- Labels
- Components
- Description from project templates

| Input | Output |
|-------|--------|
| Requirement description + Project name | Jira ticket with all fields populated |

**Acceptance Criteria:**
- [ ] User provides requirement text and project name
- [ ] System loads project-specific configuration
- [ ] System creates Jira task with correct Epic, Sprint, Labels, Components
- [ ] Description follows project template with requirement details
- [ ] System returns created ticket ID

#### FR-1.2: Per-Project Configuration
**Priority:** High | **Status:** Implemented

The system SHALL support YAML-based configuration per project defining:
- Jira project key
- Default Epic
- Sprint board
- Required labels
- Component tags
- Description templates

**Acceptance Criteria:**
- [ ] Project configs stored in `configs/projects/<project>.yaml`
- [ ] Unknown projects rejected with helpful error message
- [ ] Configs can be updated without code changes

#### FR-1.3: Bulk Task Creation
**Priority:** Medium | **Status:** Implemented

The system SHALL support creating multiple Jira tasks from a list of requirements.

**Acceptance Criteria:**
- [ ] Accept multiple requirement descriptions
- [ ] Create all tasks in single operation
- [ ] Return summary with all created ticket IDs

---

### 4.2 Development Phase - Test Evidence Collection

#### FR-2.1: Collect Test Results from CI/CD
**Priority:** High | **Status:** Implemented

The system SHALL collect test results from CI/CD pipelines:
- Dev test results
- UAT test results
- Regression test results
- Performance test results

**Acceptance Criteria:**
- [ ] Retrieve test results from CI/CD pipeline
- [ ] Format results as structured Jira comments
- [ ] Include pass/fail status and key metrics

#### FR-2.2: Attach Evidence to Jira
**Priority:** High | **Status:** Implemented

The system SHALL attach formatted test evidence to Jira tickets as comments with:
- Evidence type labels (Dev/UAT/Regression/Performance)
- Screenshots and report attachments
- Timestamps and metadata

**Acceptance Criteria:**
- [ ] Post Jira comment with evidence type tag
- [ ] Attach screenshots and report files
- [ ] Format content for readability

---

### 4.3 Testing Phase - Browser Test Automation

#### FR-3.1: React Web App UI Testing
**Priority:** High | **Status:** Implemented

The system SHALL execute browser test flows for React web applications:
- Navigate application UI
- Perform actions (click, type, wait, assert)
- Capture screenshots at each step
- Handle SSO authentication

**Acceptance Criteria:**
- [ ] Load test flow from project YAML config
- [ ] Execute steps in Playwright browser
- [ ] Capture timestamped screenshots
- [ ] Handle corporate SSO login

#### FR-3.2: Monitoring Dashboard Evidence
**Priority:** High | **Status:** Implemented

The system SHALL capture screenshots from monitoring dashboards:
- OpenSearch log dashboards with keyword search
- SpringBoot Admin health status
- Grafana metrics dashboards

**Acceptance Criteria:**
- [ ] Configure tool URLs per project
- [ ] Execute configured search queries
- [ ] Capture screenshots with context labels
- [ ] Package as structured evidence

#### FR-3.3: Video Recording & GIF Conversion
**Priority:** Medium | **Status:** Implemented

The system SHALL optionally record test execution as video and convert to GIF for preview.

**Acceptance Criteria:**
- [ ] Start/stop recording during test flow
- [ ] Save WebM video file
- [ ] Convert to GIF for lightweight preview
- [ ] Include in evidence package metadata

#### FR-3.4: Before/After Upgrade Comparison
**Priority:** Medium | **Status:** Implemented

The system SHALL support baseline and post-upgrade screenshot comparison.

**Acceptance Criteria:**
- [ ] Capture baseline screenshots before upgrade
- [ ] Capture comparison screenshots after upgrade
- [ ] Generate side-by-side HTML comparison report

#### FR-3.5: API Testing via Postman/Newman
**Priority:** Medium | **Status:** Implemented

The system SHALL execute Postman collections via Newman CLI and capture reports.

**Acceptance Criteria:**
- [ ] Run configured Postman collection
- [ ] Capture HTML/JSON test report
- [ ] Include in evidence package

---

### 4.4 Release Preparation Phase - Compliance & Documentation

#### FR-4.1: ICE Compliance Validation
**Priority:** High | **Status:** Implemented

The system SHALL validate Jira tickets against ICE (Internal Compliance Engine) standards:
- Required testing evidence (Dev, UAT, Regression, Performance)
- Required labels and tags
- Description template conformance
- CR (Change Request) details completeness
- ICE (Implementation Completion Evidence) details

**Acceptance Criteria:**
- [ ] Check for all required evidence types
- [ ] Verify label presence
- [ ] Validate description follows template
- [ ] Report gaps with remediation guidance
- [ ] Load rules from configurable YAML

#### FR-4.2: Auto-Fix Compliance Gaps
**Priority:** Medium | **Status:** Implemented

The system SHALL offer to automatically fix compliance gaps:
- Add missing labels
- Apply template structure

**Acceptance Criteria:**
- [ ] Identify missing labels/tags
- [ ] Prompt user for confirmation
- [ ] Update Jira ticket upon approval

#### FR-4.3: Release Documentation Generation
**Priority:** High | **Status:** Implemented

The system SHALL generate release documentation sections:
- Background context
- Release Notes from completed tasks
- Implementation Steps from git/PRs
- PVT Steps from project template
- Rollback Steps

**Acceptance Criteria:**
- [ ] Aggregate data from Jira tickets, git history
- [ ] Generate each documentation section
- [ ] Present for user review
- [ ] Update Jira upon confirmation

#### FR-4.4: Block Non-Compliant Releases
**Priority:** High | **Status:** Implemented

The system SHALL prevent release documentation update if ticket fails ICE compliance.

**Acceptance Criteria:**
- [ ] Run ICE compliance check before release prep
- [ ] Warn user about gaps
- [ ] Offer to run ICE Compliance Agent

---

### 4.5 Daily Documentation Retrieval - Confluence RAG

#### FR-5.1: Natural Language Document Search
**Priority:** High | **Status:** Implemented

The system SHALL accept natural language queries to search Confluence documentation.

**Acceptance Criteria:**
- [ ] Accept natural language query
- [ ] Return relevant Confluence pages with excerpts
- [ ] Include direct links to source pages

#### FR-5.2: RAG-Enhanced Semantic Retrieval
**Priority:** High | **Status:** Implemented

The system SHALL use Retrieval-Augmented Generation (RAG) with vector database for semantic search.

**Acceptance Criteria:**
- [ ] Index Confluence content in vector DB
- [ ] Return semantically similar results (not just keyword matches)
- [ ] Support different terminology than source documents

#### FR-5.3: Document Summarization
**Priority:** Medium | **Status:** Implemented

The system SHALL summarize long Confluence documents using LLM.

**Acceptance Criteria:**
- [ ] Accept page ID or URL
- [ ] Generate concise summary with key points
- [ ] Include link to full document

#### FR-5.4: Alternative Search Suggestions
**Priority:** Low | **Status:** Implemented

The system SHALL suggest alternative search terms when no results found.

**Acceptance Criteria:**
- [ ] Detect empty result set
- [ ] Generate alternative query suggestions
- [ ] Offer to re-run with suggestions

---

### 4.6 PVT (Production Verification Test)

#### FR-6.1: Scheduled PVT Health Checks
**Priority:** High | **Status:** Implemented

The system SHALL perform PVT health checks at scheduled times (e.g., after upstream maintenance).

**Acceptance Criteria:**
- [ ] Trigger PVT at configured schedule
- [ ] Execute health check steps
- [ ] Generate PVT report

#### FR-6.2: Login Page Screenshot Capture
**Priority:** High | **Status:** Implemented

The system SHALL capture login page screenshots as part of PVT.

**Acceptance Criteria:**
- [ ] Navigate to login page
- [ ] Capture screenshot
- [ ] Include in PVT report

#### FR-6.3: Keyword Search & Comparison
**Priority:** High | **Status:** Implemented

The system SHALL search for and compare keywords on specific pages during PVT.

**Acceptance Criteria:**
- [ ] Navigate to configured pages
- [ ] Search for expected keywords
- [ ] Compare against expected values
- [ ] Report pass/fail per keyword check

#### FR-6.4: Log Extraction for Secondary Confirmation
**Priority:** High | **Status:** Implemented

The system SHALL extract relevant logs from OpenSearch as secondary PVT confirmation.

**Acceptance Criteria:**
- [ ] Query OpenSearch for relevant log entries
- [ ] Extract key log patterns
- [ ] Include in PVT report

#### FR-6.5: PVT Report Generation
**Priority:** High | **Status:** Implemented

The system SHALL generate structured PVT reports with:
- Screenshots
- Keyword verification results
- Log excerpts
- Overall pass/fail status

**Acceptance Criteria:**
- [ ] Generate HTML report
- [ ] Include all evidence components
- [ ] Clear pass/fail indication

---

### 4.7 Production Support - Alert Triage

#### FR-7.1: Production Alert Triage
**Priority:** High | **Status:** Implemented

The system SHALL analyze production alerts and provide triage recommendations.

**Acceptance Criteria:**
- [ ] Accept alert details as input
- [ ] Correlate data from multiple sources
- [ ] Generate triage recommendation

#### FR-7.2: Multi-Platform Log Correlation
**Priority:** High | **Status:** Implemented

The system SHALL query and correlate data from:
- Grafana dashboards
- Prometheus metrics
- OpenSearch logs

**Acceptance Criteria:**
- [ ] Query each platform via API
- [ ] Correlate by timestamp and service
- [ ] Aggregate findings

#### FR-7.3: Triage Recommendation Categories
**Priority:** High | **Status:** Implemented

The system SHALL categorize alert triage recommendations:
- **[IGNORE]**: Transient issue, auto-recovered, safe to dismiss
- **[NEEDS ATTENTION]**: Requires investigation but not critical
- **[CRITICAL]**: Requires immediate intervention

**Acceptance Criteria:**
- [ ] Analyze alert context
- [ ] Apply LLM reasoning
- [ ] Output with exactly one category label
- [ ] Provide justification

#### FR-7.4: Alert Triage Report
**Priority:** Medium | **Status:** Implemented

The system SHALL generate alert triage reports with:
- Alert details
- Correlated log entries
- Metric summaries
- Triage recommendation
- Suggested actions

**Acceptance Criteria:**
- [ ] Generate structured report
- [ ] Include supporting evidence
- [ ] Clear recommendation display

---

### 4.8 Multi-Agent Orchestration

#### FR-8.1: Request Routing
**Priority:** High | **Status:** Implemented

The system SHALL route user requests to appropriate agents based on request type.

**Acceptance Criteria:**
- [ ] Parse user intent from CLI command
- [ ] Route to correct agent
- [ ] Pass parsed parameters

#### FR-8.2: Inter-Agent Data Flow
**Priority:** High | **Status:** Implemented

The system SHALL pass data between agents in multi-step workflows.

**Acceptance Criteria:**
- [ ] Define workflows with agent sequence
- [ ] Pass output from one agent as input to next
- [ ] Track workflow state

#### FR-8.3: Human-in-the-Loop Confirmation
**Priority:** High | **Status:** Implemented

The system SHALL request user confirmation before executing actions with side effects.

**Acceptance Criteria:**
- [ ] Preview action content
- [ ] Wait for user confirmation
- [ ] Execute or cancel based on response

#### FR-8.4: Progress Feedback
**Priority:** Medium | **Status:** Implemented

The system SHALL provide real-time progress feedback during multi-agent workflows.

**Acceptance Criteria:**
- [ ] Display current agent and step
- [ ] Show overall workflow progress
- [ ] Report completion status

---

## 5. Non-Functional Requirements

### 5.1 Architecture

| Requirement | Description |
|-------------|-------------|
| **Hexagonal Architecture** | Ports and adapters pattern for flexibility |
| **Mock/Live Mode** | Support local development with mock services |
| **Extensible Agents** | Easy to add new agents without core changes |
| **YAML Configuration** | Project and rule configs externalized from code |

### 5.2 LLM Support

| Requirement | Description |
|-------------|-------------|
| **Multi-Provider** | Support OpenAI, DashScope/Qwen, and extensible to others |
| **Configurable Models** | Model selection via YAML config |
| **API Key Management** | Secure environment variable handling |

### 5.3 Testing

| Requirement | Description |
|-------------|-------------|
| **Unit Tests** | All agents have mocked unit tests |
| **Integration Tests** | Test agent interactions with mock services |
| **E2E Tests** | Full workflow tests against mock servers |

### 5.4 Operations

| Requirement | Description |
|-------------|-------------|
| **CLI Interface** | Typer-based CLI for all operations |
| **Docker Compose** | Mock services runnable via Docker |
| **Evidence Storage** | Structured evidence output with metadata |

---

## 6. Gap Analysis: PRD vs Existing Specs

### 6.1 Fully Covered Requirements

| Requirement | Spec Location | Status |
|-------------|---------------|--------|
| Jira task creation with templates | jira-task-automation | ✅ Complete |
| Per-project YAML config | jira-task-automation | ✅ Complete |
| Bulk task creation | jira-task-automation | ✅ Complete |
| React web app UI testing | browser-test-agent | ✅ Complete |
| Monitoring dashboard screenshots | browser-test-agent | ✅ Complete |
| SSO authentication handling | browser-test-agent | ✅ Complete |
| Before/after upgrade comparison | browser-test-agent | ✅ Complete |
| Evidence packaging | browser-test-agent, evidence-gathering | ✅ Complete |
| Newman API testing | browser-test-agent | ✅ Complete |
| ICE compliance validation | ice-compliance-validation | ✅ Complete |
| Auto-fix labels/tags | ice-compliance-validation | ✅ Complete |
| Description template validation | ice-compliance-validation | ✅ Complete |
| Configurable ICE rules | ice-compliance-validation | ✅ Complete |
| Test result collection from CI/CD | evidence-gathering | ✅ Complete |
| Attach evidence to Jira | evidence-gathering | ✅ Complete |
| Release documentation generation | release-prep | ✅ Complete |
| Block non-compliant releases | release-prep | ✅ Complete |
| Confluence search with RAG | confluence-doc-retrieval | ✅ Complete |
| Document summarization | confluence-doc-retrieval | ✅ Complete |
| PVT health checks | log-analysis-and-pvt | ✅ Complete |
| Alert triage with correlation | log-analysis-and-pvt | ✅ Complete |
| Multi-platform querying | log-analysis-and-pvt | ✅ Complete |
| Request routing | agent-coordinator | ✅ Complete |
| Inter-agent data flow | agent-coordinator | ✅ Complete |
| Human-in-the-loop confirmation | agent-coordinator | ✅ Complete |

### 6.2 Partially Covered / Needs Enhancement

| PRD Requirement | Current Spec Coverage | Gap |
|-----------------|----------------------|-----|
| FR-5.4: Alternative search suggestions | Not explicitly mentioned | Spec exists but PRD adds detail |
| Video recording & GIF conversion | Briefly mentioned | PRD formalizes requirements |
| Progress feedback | Mentioned but brief | PRD formalizes requirements |

### 6.3 Missing from Existing Specs

| PRD Requirement | Gap Description |
|-----------------|-----------------|
| **Multi-LLM Provider Support** | PRD adds explicit requirement for OpenAI, DashScope/Qwen support. Specs assume single provider. |
| **Evidence Summary Report** | PRD describes HTML evidence summary report generation. Not in specs. |
| **Scheduled PVT Execution** | PRD mentions "scheduled times" but specs focus on manual trigger. Cron/scheduling not specified. |

---

## 7. Recommendations

### 7.1 Spec Updates Needed

1. **Add LLM Provider Configuration Spec**
   - Create `llm-provider` spec document
   - Define provider interface, config schema, factory pattern

2. **Formalize Evidence Reporting**
   - Add evidence summary HTML generation to browser-test-agent or evidence-gathering spec

3. **Define Scheduling Mechanism**
   - Add scheduled execution capability to log-analysis-and-pvt spec
   - Consider cron-based or external trigger mechanism

### 7.2 Implementation Priority

| Priority | Feature | Rationale |
|----------|---------|-----------|
| P0 | Multi-LLM provider support | Already implemented, needs spec documentation |
| P1 | Evidence summary report | Already implemented, useful for users |
| P2 | Scheduled PVT execution | Enhancement for automation |

---

## 8. Appendix

### A. Project Configuration Schema

```yaml
# configs/projects/<project>.yaml
name: "Project Name"
type: react-app | backend

jira:
  project_key: "PROJ"
  epic: "PROJ-100"
  sprint_board: "Sprint Board Name"
  labels: ["label1", "label2"]
  components: ["Component1", "Component2"]
  description_template: |
    h2. Background
    {background}

    h2. Requirements
    {requirements}

tool_urls:
  opensearch: "http://opensearch.instance"
  springboot_admin: "http://sba.instance"
  grafana: "http://grafana.instance"

evidence_checks:
  opensearch:
    - name: "Error Logs"
      query: "service:project AND level:ERROR"
      screenshot_label: "error_logs"

test_flows:
  - name: "User Login Flow"
    steps:
      - action: navigate
        target: "https://app.example.com/login"
      - action: screenshot
        label: "login_page"
```

### B. ICE Rules Configuration Schema

```yaml
# configs/ice_rules.yaml
required_labels:
  - ice-compliant
  - release-approved

required_description_sections:
  - Background
  - Implementation
  - Rollback Plan

required_evidence:
  - type: dev
    label: "Dev Testing"
    required: true
  - type: uat
    label: "UAT Testing"
    required: true
  - type: regression
    label: "Regression Testing"
    required: true
  - type: performance
    label: "Performance Testing"
    required: false

cr_fields:
  - field: rollback_plan
    description: "Rollback Plan"
    required: true
  - field: implementation_steps
    description: "Implementation Steps"
    required: true
```

### C. LLM Provider Configuration

```yaml
# configs/app.yaml
llm_provider: openai | dashscope
llm_model: gpt-4o | qwen-plus | qwen-max
```

```bash
# Environment Variables
export OPENAI_API_KEY="sk-..."      # For OpenAI provider
export DASHSCOPE_API_KEY="sk-..."   # For DashScope/Qwen provider
```