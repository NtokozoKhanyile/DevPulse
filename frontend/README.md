# DevPulse

> Build in public. Ship with confidence.

DevPulse is a social SaaS platform where developers share what they're building, track progress with milestones, find collaborators, and celebrate shipping — all in real time.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Available Scripts](#available-scripts)
- [API Reference](#api-reference)
- [WebSocket Feed](#websocket-feed)
- [Design System](#design-system)
- [Page Routes](#page-routes)
- [Component Architecture](#component-architecture)
- [State Management](#state-management)
- [Authentication Flow](#authentication-flow)
- [Deployment](#deployment)
- [Contributing](#contributing)

---

## Overview

DevPulse consists of three layers, each owned by a separate team:

| Layer | Technology | Status |
|-------|-----------|--------|
| Database | PostgreSQL 15, SQLAlchemy 2.0 async | ✅ Complete |
| Backend API | Python 3.13, FastAPI 0.115.5 | ✅ Complete |
| Frontend SPA | React 18, Vite 5, Tailwind CSS | ✅ Complete |

This repository documents the **frontend** layer. The backend exposes 33 REST endpoints and a WebSocket live feed. The frontend consumes both.

---

## Features

### 1. Developer Accounts
- Register with username, email, display name, and password
- Public profile with bio, skills, GitHub and website links
- Avatar upload (JPEG / PNG / WebP, max 5 MB)
- Password strength indicator on registration

### 2. Project Entries
- Create projects with title, description, stage, tech stack, and support tags
- Cover image upload
- Repository and live URL links
- Markdown-rendered descriptions

### 3. Live Feed
- Real-time WebSocket feed of all platform activity
- Five event types: `project_created`, `milestone_posted`, `project_completed`, `comment_posted`, `collab_request`
- HTTP fallback on initial load
- Connection indicator with automatic reconnection (up to 5 attempts)
- Feed capped at 100 events to prevent memory growth

### 4. Collaboration
- Comment on any project with threaded replies
- Edit comments within 15 minutes of posting
- Soft-deleted comments preserved as `[comment deleted]` to maintain thread structure
- Raise hand to collaborate with an optional message
- Project owners accept or decline requests from their profile

### 5. Celebration Wall
- Public wall of all completed projects — no authentication required
- Confetti animation on first load
- Featured entries pinned at the top
- Owner shoutout messages
- Share button copies project URL to clipboard
- Paginated with load more

### 6. Project Stage Tracking
Projects move through five stages in order:

```
idea → building → testing → shipped → completed
```

`completed` is terminal and irreversible. Completing a project automatically creates a Celebration Wall entry.

---

## Tech Stack

| Concern | Choice | Version |
|---------|--------|---------|
| Framework | React | 18.3.1 |
| Build tool | Vite | 5.4.8 |
| Routing | React Router | 6.26.2 |
| State | Zustand | 5.0.1 |
| HTTP client | Axios | 1.7.7 |
| Forms | React Hook Form | 7.53.1 |
| Styling | Tailwind CSS | 3.4.14 |
| Icons | Lucide React | 0.460.0 |
| Markdown | React Markdown | 9.0.1 |
| Utilities | clsx | 2.1.1 |

---

## Project Structure

```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── .env.local                         ← local env vars (gitignored)
│
└── src/
    ├── main.jsx                       ← React entry point
    ├── App.jsx                        ← Router + layout shell + ProtectedRoute
    │
    ├── pages/
    │   ├── Landing.jsx                ← Public home, wall preview, stats
    │   ├── Login.jsx                  ← Auth with redirect-after-login
    │   ├── Register.jsx               ← Auth with password strength indicator
    │   ├── Feed.jsx                   ← Live WebSocket feed + HTTP fallback
    │   ├── ProjectDetail.jsx          ← Full project view, milestones, comments
    │   ├── NewProject.jsx             ← Project creation form
    │   ├── EditProject.jsx            ← Project edit form
    │   ├── Profile.jsx                ← Own (editable) + others' (read-only)
    │   ├── CelebrationWall.jsx        ← Public wall, no auth required
    │   └── NotFound.jsx
    │
    ├── components/
    │   ├── ui/                        ← Design system primitives
    │   │   ├── Button.jsx
    │   │   ├── Input.jsx
    │   │   ├── Textarea.jsx
    │   │   ├── Select.jsx
    │   │   ├── Badge.jsx              ← Stage pills + support tags
    │   │   ├── Avatar.jsx             ← Image or initials fallback
    │   │   ├── Modal.jsx              ← Focus-trapped, Escape-dismissible
    │   │   ├── Toast.jsx              ← Provider + hook, no external library
    │   │   ├── Spinner.jsx
    │   │   └── EmptyState.jsx
    │   │
    │   ├── layout/
    │   │   ├── Navbar.jsx             ← Sticky dark navbar, notification badge
    │   │   ├── Sidebar.jsx            ← Support tags, wall CTA, notifications
    │   │   └── PageWrapper.jsx
    │   │
    │   ├── feed/
    │   │   ├── FeedCard.jsx           ← Renders all 5 WebSocket event types
    │   │   ├── FeedList.jsx           ← aria-live region
    │   │   └── ConnectionIndicator.jsx
    │   │
    │   ├── project/
    │   │   ├── ProjectCard.jsx        ← Cover, stage badge, tech pills, owner
    │   │   ├── StageSelector.jsx      ← Horizontal step selector with progress line
    │   │   ├── MilestoneList.jsx      ← Vertical timeline
    │   │   ├── MilestoneForm.jsx      ← Inline milestone posting
    │   │   ├── CollabButton.jsx       ← 4 states: default, pending, accepted, hidden
    │   │   └── TagInput.jsx           ← Enter/comma tag input with backspace delete
    │   │
    │   ├── comments/
    │   │   ├── CommentThread.jsx      ← Threaded replies, edit, soft delete
    │   │   └── CommentInput.jsx       ← Expanding textarea, authenticated only
    │   │
    │   └── wall/
    │       ├── WallCard.jsx           ← Featured badge, share button, shoutout
    │       └── WallGrid.jsx           ← Grid layout with load more pagination
    │
    ├── store/                         ← Zustand state slices
    │   ├── authStore.js               ← Persisted auth state (localStorage)
    │   ├── feedStore.js               ← Live events, connection state
    │   └── notificationStore.js       ← Notifications + unread count
    │
    ├── hooks/
    │   ├── useAuth.js                 ← Login, logout, register actions
    │   ├── useFeed.js                 ← WebSocket with reconnect logic
    │   └── useProject.js              ← Fetch, create, update, complete
    │
    ├── api/                           ← Axios client + endpoint modules
    │   ├── client.js                  ← Axios instance, request + refresh interceptors
    │   ├── auth.js
    │   ├── users.js
    │   ├── projects.js
    │   ├── comments.js
    │   ├── collaborations.js
    │   ├── wall.js
    │   ├── notifications.js
    │   └── index.js                   ← Barrel export
    │
    └── styles/
        ├── globals.css                ← CSS variables, reset, base typography
        └── theme.js                   ← JS design tokens, stageColors, STAGE_ORDER
```

---

## Getting Started

### Prerequisites

| Tool | Version |
|------|---------|
| Node.js | 20 LTS or higher |
| npm | 10 or higher |
| Backend API | Running on `http://localhost:8000` |

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd devpulse

# Install frontend dependencies
cd frontend
npm install

# Create your local environment file
cp .env.local.example .env.local
# Edit .env.local with your values

# Start the development server
npm run dev
```

The app will be available at `http://localhost:5173`.

The Vite dev server proxies all `/api` requests to `http://localhost:8000`, so no CORS configuration is needed during development.

### Backend dependency

The frontend requires the DevPulse backend to be running. Swagger UI is available at `http://localhost:8000/api/docs` — use this to inspect request and response shapes during development.

---

## Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/api/v1/feed/ws
```

All Vite environment variables must be prefixed with `VITE_` to be accessible in the browser bundle.

> **Never commit `.env.local`.** It is gitignored by default.

---

## Available Scripts

Run these from inside the `frontend/` directory.

| Script | Description |
|--------|-------------|
| `npm run dev` | Start Vite dev server on port 5173 with HMR |
| `npm run build` | Production build to `dist/` |
| `npm run preview` | Preview the production build locally |

---

## API Reference

The backend exposes 33 endpoints across 9 routers. All endpoints are prefixed with `/api/v1`.

### Authentication — `/auth`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | None | Register. Returns token pair. |
| POST | `/auth/login` | None | Login. Returns token pair. |
| POST | `/auth/refresh` | None | Body: `{ refresh_token }`. Returns new token pair. |
| POST | `/auth/logout` | Bearer | Blacklists refresh token. |

### Users — `/users`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/users/me` | Bearer | Current user (private). |
| PATCH | `/users/me` | Bearer | Update profile fields. |
| POST | `/users/me/avatar` | Bearer | Upload avatar. Multipart form. |
| GET | `/users/{username}` | None | Public profile. |
| GET | `/users/{username}/projects` | None | User's public projects. |

### Projects — `/projects`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/projects` | Bearer | Create project. |
| GET | `/projects` | None | Paginated project list. |
| GET | `/projects/{id}` | None | Single project. Increments `view_count`. |
| PATCH | `/projects/{id}` | Bearer | Partial update. Owner only. |
| DELETE | `/projects/{id}` | Bearer | Delete. Owner only. |
| POST | `/projects/{id}/complete` | Bearer | Mark complete. Irreversible. Owner only. |
| POST | `/projects/{id}/cover` | Bearer | Upload cover image. Multipart form. |

### Milestones — `/projects/{id}/milestones`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/projects/{id}/milestones` | Bearer | Post milestone. Publishes to feed. |
| GET | `/projects/{id}/milestones` | None | List milestones, chronological order. |

### Comments — `/projects/{id}/comments`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/projects/{id}/comments` | Bearer | Post comment. `parent_id` optional for replies. |
| GET | `/projects/{id}/comments` | None | Paginated. Soft-deleted show empty body. |
| PATCH | `/projects/{id}/comments/{cid}` | Bearer | Edit. Author only. Within 15 min. |
| DELETE | `/projects/{id}/comments/{cid}` | Bearer | Soft delete. Author or project owner. |

### Collaborations — `/projects/{id}/collaborate`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/projects/{id}/collaborate` | Bearer | Raise hand. Cannot request own project. |
| GET | `/projects/{id}/collaborate` | Bearer | List requests. Owner only. |
| PATCH | `/projects/{id}/collaborate/{rid}` | Bearer | Accept or decline. Owner only. |

### Celebration Wall — `/wall`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/wall` | None | Paginated. Featured first. |
| GET | `/wall/{id}` | None | Single entry. |
| PATCH | `/wall/{id}/shoutout` | Bearer | Add shoutout. Project owner only. |

### Notifications — `/notifications`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/notifications` | Bearer | List notifications. |
| PATCH | `/notifications/{id}/read` | Bearer | Mark single read. |
| PATCH | `/notifications/read-all` | Bearer | Mark all read. |
| GET | `/notifications/unread-count` | Bearer | Returns `{ count: number }`. |

### Pagination

All list endpoints accept `?page=1&limit=20`. Default limit is 20, max is 100.

---

## WebSocket Feed

The live feed connects via WebSocket. Authentication is passed as a query parameter — the WebSocket handshake cannot carry HTTP headers.

```
ws://localhost:8000/api/v1/feed/ws?token=<access_token>
```

### Connection behaviour

- Reconnects automatically up to 5 times on disconnect (3 second delay between attempts)
- Close code `4001` = authentication failure — does not attempt reconnect
- Feed events are capped at 100 items in the store to prevent memory growth
- `aria-live="polite"` region announces new events to screen readers

### Event types

All events share a common shape:

```javascript
{
  type:      string,   // event type (see below)
  timestamp: string,   // ISO 8601
  // ...event-specific fields
}
```

| Event type | Additional fields |
|-----------|------------------|
| `project_created` | `project_id`, `owner_id`, `title`, `stage` |
| `milestone_posted` | `project_id`, `owner_id`, `milestone_title` |
| `project_completed` | `project_id`, `owner_id`, `title` |
| `comment_posted` | `project_id`, `author_id` |
| `collab_request` | `project_id`, `requester_id` |

---

## Design System

### Brand colours

| Token | Hex | Usage |
|-------|-----|-------|
| `brand.primary` | `#1A7A3E` | Primary actions, links, active states |
| `brand.accent` | `#639922` | Success, highlights |
| `brand.tint` | `#E8F5EE` | Light fills, tag backgrounds |
| `brand.border` | `#C6E6D2` | Green-tinted borders |
| `surface.white` | `#FFFFFF` | Cards, inputs |
| `surface.offwhite` | `#F9FAFB` | Page backgrounds |
| `surface.dark` | `#111111` | Navbar, footer |
| `text.primary` | `#111111` | Headings |
| `text.body` | `#374151` | Body copy |
| `text.muted` | `#6B7280` | Captions, placeholders |
| `ui.border` | `#D1D5DB` | Default borders |
| `ui.error` | `#DC2626` | Error states |

No blues. No purples. No teals. Green, white, black — executed consistently.

### Stage badge colours

| Stage | Background | Text | Border |
|-------|-----------|------|--------|
| `idea` | `#F3F4F6` | `#374151` | `#D1D5DB` |
| `building` | `#E8F5EE` | `#1A7A3E` | `#C6E6D2` |
| `testing` | `#FFF7ED` | `#92400E` | `#FDE68A` |
| `shipped` | `#EFF6FF` | `#1E40AF` | `#BFDBFE` |
| `completed` | `#F0FFF4` | `#166534` | `#BBF7D0` |

### Typography

- **UI font:** Inter (Google Fonts)
- **Monospace:** JetBrains Mono (code blocks, inline code)

### Accessibility

- Colour contrast meets WCAG AA (4.5:1 normal text, 3:1 large text)
- All form inputs have associated `<label>` elements
- Modal dialogs trap focus and close on Escape
- Live feed region uses `aria-live="polite"`
- All images have `alt` attributes
- All interactive elements are keyboard accessible

---

## Page Routes

| Path | Auth | Page |
|------|------|------|
| `/` | Public | Landing |
| `/login` | Public | Login |
| `/register` | Public | Register |
| `/wall` | Public | Celebration Wall |
| `/profile/:username` | Public | Profile (read-only) |
| `/projects/:id` | Public | Project Detail |
| `/feed` | **Required** | Live Feed |
| `/projects/new` | **Required** | New Project |
| `/projects/:id/edit` | **Required** | Edit Project |
| `/profile/me` | **Required** | Own Profile (editable) |

Unauthenticated users attempting to access protected routes are redirected to `/login?redirect=<original_path>`. After login they are returned to the original path.

---

## Component Architecture

### Rules enforced across all components

- **Single responsibility.** One component does one thing. Two responsibilities = two components.
- **200 line limit.** No component file exceeds 200 lines. Extract sub-components when this is reached.
- **No direct API calls in components.** API calls live in hooks or are triggered via store actions.
- **No inline styles.** Tailwind utility classes only, unless a dynamic value is unavoidable.
- **`React.memo` on list items.** `FeedCard`, `ProjectCard`, `WallCard`, `CommentItem` are all memoised to prevent unnecessary re-renders during feed updates.
- **`loading="lazy"` on images.** All images not guaranteed to be above the fold use lazy loading.

### Naming conventions

| Target | Convention | Example |
|--------|-----------|---------|
| Component files | PascalCase | `FeedCard.jsx` |
| Hook files | camelCase, `use` prefix | `useFeed.js` |
| Store files | camelCase | `authStore.js` |
| CSS classes | kebab-case | `.feed-card` (Tailwind utilities exempt) |
| JS variables/functions | camelCase | `handleSubmit` |

---

## State Management

Three Zustand stores manage all shared state.

### `authStore` — persisted to localStorage

```javascript
{
  user:            object | null,
  accessToken:     string | null,
  refreshToken:    string | null,
  isAuthenticated: boolean,
}
```

### `feedStore` — ephemeral

```javascript
{
  events:          array,    // max 100 items
  isConnected:     boolean,
  connectionError: string | null,
}
```

### `notificationStore` — ephemeral

```javascript
{
  notifications: array,
  unreadCount:   number,
}
```

---

## Authentication Flow

### Token lifecycle

- **Access token:** 30 minute TTL. Attached to every request via Axios request interceptor.
- **Refresh token:** 7 day TTL. Stored in Zustand persisted to localStorage. Sent in request body (not Authorization header) to `POST /auth/refresh`.

### Silent refresh

When a request returns `401`, the Axios response interceptor:

1. Pauses all in-flight requests
2. Calls `POST /auth/refresh` with the stored refresh token
3. Updates the store with new tokens
4. Retries all paused requests with the new access token
5. If refresh fails, clears auth state and redirects to `/login`

This means components never handle token expiry — it is invisible to the UI.

### Key gotchas

- **WebSocket auth is via query param** — the handshake cannot carry headers
- **Refresh token goes in the request body** — not the Authorization header
- **Completed projects are irreversible** — `POST /projects/{id}/complete` locks the stage permanently
- **Soft-deleted comments preserve thread structure** — render as `[comment deleted]`, never hide
- **`view_count` increments on every GET** — call `GET /projects/{id}` once on mount only

---

## Deployment

### Production build

```bash
cd frontend
npm run build
```

Output is in `frontend/dist/`. This is a static SPA — serve `dist/` from any static host (Vercel, Netlify, S3, nginx).

### nginx example config

```nginx
server {
  listen 80;
  root /var/www/devpulse/dist;
  index index.html;

  # Proxy API and WebSocket to backend
  location /api/ {
    proxy_pass http://localhost:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
  }

  # SPA fallback — all routes serve index.html
  location / {
    try_files $uri $uri/ /index.html;
  }
}
```

### Environment variables for production

Set these in your hosting provider's environment config — not in a committed file:

```bash
VITE_API_BASE_URL=https://api.yourdevpulsedomain.com/api/v1
VITE_WS_URL=wss://api.yourdevpulsedomain.com/api/v1/feed/ws
```

Note `wss://` (secure WebSocket) for production.

---

## Contributing

### Before you write any code

1. Read this README fully
2. Read `DevPulse_Frontend_Team_Instructions.md`
3. Inspect the backend Swagger UI at `http://localhost:8000/api/docs`
4. Check the browser console — zero errors is the baseline

### Commit convention

```
feat(frontend): short description of what was built
fix(frontend): short description of what was fixed
refactor(frontend): short description of what was restructured
```

### Pull request checklist

- [ ] `npm run build` completes with zero errors and zero warnings
- [ ] All pages tested end-to-end as a real user
- [ ] WebSocket tested across two browser tabs
- [ ] Token refresh tested by manually expiring the access token in DevTools
- [ ] `/wall` tested in incognito — loads without any auth
- [ ] All forms validated — inline errors appear, no submit on invalid state
- [ ] All empty states handled — no blank screens
- [ ] All loading states handled — no blank screens while data loads
- [ ] Responsive tested at 375px, 768px, and 1280px

---

*DevPulse Frontend — built in public, shipped with confidence.*