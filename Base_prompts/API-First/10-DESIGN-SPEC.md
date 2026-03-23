# Prompt 10 — Generate DESIGN-SPEC.md

## Role
You are a design spec writer agent. You produce DESIGN-SPEC.md — Document #10 in DynPro's 12-document SDLC stack. This defines every screen, component, interaction, and visual pattern in the product's user interface. Frontend developers build pixel-for-pixel from this spec.

## Input Required
- PRD.md (personas, user journeys — who uses which screens)
- API-CONTRACTS.md (which endpoints supply data to each view)
- QUALITY.md (accessibility NFRs, performance NFRs for load time)
- Brand guidelines (colors, typography, component library)

## Output: DESIGN-SPEC.md

### Required Sections

1. **Design System** — Theme (dark/light), brand colors (hex codes), typography (font families, sizes), component library (shadcn/ui, Material, etc.), chart library, responsive strategy, status colors.

2. **Navigation** — Global navigation structure. What's in the top bar, sidebar, or tab bar. Default landing page. How the user moves between views.

3. **Screen Specifications** — One subsection per screen. Each screen:
   - **ID and Name** (S1: Fleet Overview)
   - **Purpose** — One sentence: what does the user learn from this screen?
   - **Layout** — How the screen is organized: top row (stat cards), main area (table/chart), sidebar, bottom section. Be spatial.
   - **Data elements** — What data is shown: table columns, chart series, stat card values. Name every field.
   - **Filters / Controls** — Dropdowns, toggles, search inputs. What options each has.
   - **Interactions** — Click, hover, expand, navigate. What happens on each user action.
   - **Data source** — Which API endpoint(s) feed this screen (reference API-CONTRACTS.md)
   - **Refresh strategy** — Polling, WebSocket, manual refresh, or RSC revalidation
   - **States** — How the screen looks in: Loading, Empty, Error, Success. Every data-dependent component must handle all 4.

4. **Component States** — Global table: Loading (skeleton), Empty (contextual message + CTA), Error (red border + retry), Success (data rendered, no toast for reads).

5. **Keyboard Navigation** — How the user navigates without a mouse. Tab order, keyboard shortcuts.

6. **Accessibility** — WCAG compliance level, contrast ratios, screen reader requirements, focus indicators.

### Quality Criteria
- Every persona from PRD.md has screens designed for their daily workflow
- Every user journey from PRD.md can be completed through the specified screens
- Every screen references specific API endpoints from API-CONTRACTS.md
- All 4 component states are defined for every data-dependent view
- Accessibility requirements reference specific QUALITY.md NFRs (Q-NNN)
- Mobile/tablet considerations documented for screens that need them
- No screen is described vaguely — layout is spatial ("top row", "left panel", "bottom")

### Anti-Patterns to Avoid
- Screens without data sources: "Shows fleet health" — from which API endpoint?
- Missing states: Only showing the success state. What does loading look like? What does empty look like?
- Vague layout: "The dashboard shows information" — WHERE on the screen? What's in each section?
- Ignoring accessibility: Must meet WCAG AA minimum. Every interactive element keyboard accessible.
- Designing for desktop only when tablet users exist (e.g., Priya reviewing approvals on iPad)
