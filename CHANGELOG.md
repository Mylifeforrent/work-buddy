# Changelog

All notable changes to Work Buddy will be documented in this file.

## [Unreleased]

### Added

#### Evidence Generation Improvements
- **Visible Mouse Cursor in Recordings**: Video recordings now show a cursor overlay that moves to each element before clicking, making test flows easy to follow
- **Click Animation**: Cursor changes color (red to green) and scales up when clicking to highlight interactions
- **GIF Conversion**: Videos are automatically converted to animated GIF format for easy sharing and embedding in reports
- **HTML Evidence Summary Report**: Comprehensive summary of all evidence packages with screenshots, status indicators, and metadata

#### Mock React UI Enhancements
- **Professional Enterprise Styling**: Complete redesign with Ant Design ConfigProvider theming, shadows, gradients, and proper spacing
- **Dashboard Page**: Statistics cards with icons, performance charts, user activity progress bars, and recent orders list
- **Data List Page**: Row selection, progress bars, action buttons with tooltips, and enhanced search/filter UI
- **Form Page**: Two-column layout, form guidelines sidebar, recent submissions list, and loading states
- **Analytics Page**: Metric cards with trend indicators, comparative bar charts, system health progress bars
- **Collapsible Sidebar**: Navigation sidebar with gradient header and collapse functionality
- **Notification Badge**: Header shows notification count with bell icon
- **Visual Feedback**: Hover states, loading spinners, and transition animations throughout

### Changed
- Updated `convert_to_gif()` method to properly detect and use ffmpeg path
- Simplified GIF conversion logic for improved reliability
- Re-inject cursor overlay after page navigation during recordings

### Requirements
- **ffmpeg** is required for GIF conversion (optional - videos will still be generated without it)
  - Install on macOS: `brew install ffmpeg`
  - Install on Ubuntu: `sudo apt-get install ffmpeg`
  - Install on Windows: `choco install ffmpeg`

## [0.1.0] - 2026-03-23

### Added
- Multi-provider LLM support (OpenAI, DashScope/Qwen) with factory pattern
- Cron-based PVT scheduling with timezone support
- Per-project PVT schedule configuration with enable/disable switch
- Browser test agent with video recording and GIF conversion
- ICE compliance validation agent
- Jira task automation agent
- Confluence RAG agent for document search
- Log analyst agent for alert triage
- Release preparation agent
- Mock services for local development (Jira, Confluence, SSO)
- Typer-based CLI interface