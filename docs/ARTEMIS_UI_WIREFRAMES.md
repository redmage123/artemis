# Artemis UI - Wireframes
**Version:** 1.0
**Date:** 2025-10-26

---

## Table of Contents

1. [Layout Shell](#1-layout-shell)
2. [Dashboard](#2-dashboard)
3. [Kanban Board](#3-kanban-board)
4. [Task Detail Modal](#4-task-detail-modal)
5. [Pipeline Monitoring](#5-pipeline-monitoring)
6. [Code Review](#6-code-review)
7. [Sprint Planning](#7-sprint-planning)
8. [Sprint Detail](#8-sprint-detail)
9. [RAG Knowledge Browser](#9-rag-knowledge-browser)
10. [Settings Pages](#10-settings-pages)
11. [Mobile Views](#11-mobile-views)

---

## Wireframe Legend

```
┌─────┐   Border/Container
│     │
└─────┘

[Button]   Clickable button
<Input>    Text input field
▼          Dropdown
⚙          Icon
═══        Divider line
...        Scrollable area
```

---

## 1. Layout Shell

### Desktop Layout (1440px+ wide)
```
┌────────────────────────────────────────────────────────────────────────────────┐
│ ┌─Logo──┬────────────────────────────────────────────────┬─[User]─[🔔]─[⚙]─┐ │
│ │ ARTEMIS│   <Search projects, tasks...>                  │                  │ │
│ └────────┴────────────────────────────────────────────────┴──────────────────┘ │
├─────────────┬──────────────────────────────────────────────────────────────────┤
│             │                                                                  │
│ ┌─Nav────┐ │                                                                  │
│ │         │ │                     MAIN CONTENT AREA                           │
│ │ 🏠 Dash │ │                                                                  │
│ │ 📋 Board│ │                  (Content changes per page)                     │
│ │ 📅 Sprint│ │                                                                  │
│ │ 📚 Know │ │                                                                  │
│ │ ⚙ Settings││                                                                │
│ │         │ │                                                                  │
│ │         │ │                                                                  │
│ │         │ │                                                                  │
│ │         │ │                                                                  │
│ │         │ │                                                                  │
│ │         │ │                                                                  │
│ │ [Collapse│ │                                                                 │
│ └─────────┘ │                                                                  │
└─────────────┴──────────────────────────────────────────────────────────────────┘
   240px wide  Fluid (responsive)
```

### Sidebar States

**Expanded (240px):**
```
┌─────────────┐
│ 🏠 Dashboard│
│ 📋 Board    │
│ 📅 Sprints  │
│ 📚 Knowledge│
│ ⚙ Settings  │
│             │
│             │
│ [⬅ Collapse]│
└─────────────┘
```

**Collapsed (64px):**
```
┌──┐
│🏠│
│📋│
│📅│
│📚│
│⚙ │
│  │
│  │
│➡ │
└──┘
```

### Header Component
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ┌─────────┬──────────────────────────────────────┬────────────────────────┐ │
│ │ ARTEMIS │   🔍 <Search...>   [Cmd+K]           │ [User Avatar ▼] [🔔] │ │
│ └─────────┴──────────────────────────────────────┴────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

**User Dropdown Menu:**
```
┌─────────────────────┐
│ John Doe            │
│ john@example.com    │
├─────────────────────┤
│ 👤 Profile          │
│ ⚙  Settings         │
│ 📊 Usage Stats      │
├─────────────────────┤
│ 🚪 Logout           │
└─────────────────────┘
```

**Notifications Panel:**
```
┌──────────────────────────────────────────┐
│ Notifications                     [Clear]│
├──────────────────────────────────────────┤
│ ✅ Task "Auth API" completed             │
│    2 minutes ago                         │
├──────────────────────────────────────────┤
│ 📝 Review needed: "User Dashboard"       │
│    15 minutes ago                        │
├──────────────────────────────────────────┤
│ 🚀 Pipeline started for "Payment API"    │
│    1 hour ago                            │
├──────────────────────────────────────────┤
│ [View All Notifications]                 │
└──────────────────────────────────────────┘
```

---

## 2. Dashboard

### Full Dashboard Layout
```
┌────────────────────────────────────────────────────────────────────────────────┐
│ Dashboard                                                                      │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│ ┌─Quick Stats─────────────────────────────────────────────────────────────┐   │
│ │                                                                          │   │
│ │ ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                │   │
│ │ │   24     │  │   12     │  │   87%    │  │   6      │                │   │
│ │ │ Active   │  │ This Week│  │ Success  │  │ Sprint   │                │   │
│ │ │ Tasks    │  │ Completed│  │ Rate     │  │ Progress │                │   │
│ │ └──────────┘  └──────────┘  └──────────┘  └──────────┘                │   │
│ └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                │
│ ┌─Recent Tasks────────────────┐  ┌─Active Pipelines────────────────────┐    │
│ │                              │  │                                      │    │
│ │ 🔵 Implement user auth       │  │ 🟡 Task #142 - In Progress         │    │
│ │    Created 2h ago            │  │    Stage: Development (60%)        │    │
│ │    [View] [Run Pipeline]     │  │    [View Details]                  │    │
│ │                              │  ├──────────────────────────────────────┤    │
│ │ 🟢 Fix login bug             │  │ 🟢 Task #138 - Completed           │    │
│ │    Created 5h ago            │  │    Duration: 12m 34s               │    │
│ │    [View] [Run Pipeline]     │  │    [View Artifacts]                │    │
│ │                              │  └──────────────────────────────────────┘    │
│ │ 🟡 Add payment API           │                                             │
│ │    Created 1d ago            │  ┌─Recent Activity──────────────────────┐   │
│ │    [View] [Run Pipeline]     │  │                                      │   │
│ │                              │  │ • Code review approved for #138      │   │
│ │ 🔴 Optimize database         │  │   5 minutes ago                      │   │
│ │    Created 2d ago            │  │                                      │   │
│ │    [View] [Run Pipeline]     │  │ • Sprint "Q4 Goals" started         │   │
│ │                              │  │   1 hour ago                         │   │
│ │ [View All Tasks]             │  │                                      │   │
│ └──────────────────────────────┘  │ • Task #136 moved to Done           │   │
│                                    │   3 hours ago                        │   │
│                                    │                                      │   │
│                                    │ [View All Activity]                  │   │
│                                    └──────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Quick Stats Cards (Detail)
```
┌──────────────┐
│     24       │  ← Large number (2.5rem)
│  Active      │  ← Label (1rem)
│  Tasks       │
└──────────────┘
   Hover: Slight lift + shadow
   Click: Navigate to filtered board
```

---

## 3. Kanban Board

### Full Board View
```
┌────────────────────────────────────────────────────────────────────────────────┐
│ Kanban Board                                                    [+ New Task]   │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│ ┌─Filters/Search──────────────────────────────────────────────────────────┐   │
│ │ 🔍 <Search tasks...>  [Labels ▼]  [Priority ▼]  [Assignee ▼]  [Clear]  │   │
│ └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                │
│ ┌─BACKLOG───┐  ┌─IN PROGRESS┐  ┌─REVIEW─────┐  ┌─DONE───────┐              │
│ │  (12) +   │  │  (5)   +   │  │  (3)   +   │  │  (24)  +   │              │
│ ├───────────┤  ├────────────┤  ├────────────┤  ├────────────┤              │
│ │           │  │            │  │            │  │            │              │
│ │ ┌───────┐ │  │ ┌────────┐ │  │ ┌────────┐ │  │ ┌────────┐ │              │
│ │ │ #142  │ │  │ │ #139   │ │  │ │ #137   │ │  │ │ #135   │ │              │
│ │ │       │ │  │ │🔴 HIGH │ │  │ │        │ │  │ │        │ │              │
│ │ │ Auth  │ │  │ │Payment │ │  │ │Dashboard│ │  │ │Login   │ │              │
│ │ │ System│ │  │ │API     │ │  │ │UI      │ │  │ │Fix     │ │              │
│ │ │       │ │  │ │        │ │  │ │        │ │  │ │        │ │              │
│ │ │🏷️ auth│ │  │ │🏷️ api  │ │  │ │🏷️ ui   │ │  │ │🏷️ bug  │ │              │
│ │ └───────┘ │  │ │Running │ │  │ │        │ │  │ │        │ │              │
│ │           │  │ │⏱️ 45%  │ │  │ │        │ │  │ │✅      │ │              │
│ │ ┌───────┐ │  │ └────────┘ │  │ └────────┘ │  │ └────────┘ │              │
│ │ │ #141  │ │  │            │  │            │  │            │              │
│ │ │       │ │  │ ┌────────┐ │  │ ┌────────┐ │  │ ┌────────┐ │              │
│ │ │ Email │ │  │ │ #138   │ │  │ │ #136   │ │  │ │ #134   │ │              │
│ │ │Notifs │ │  │ │        │ │  │ │        │ │  │ │        │ │              │
│ │ │       │ │  │ │Search  │ │  │ │Profile │ │  │ │API     │ │              │
│ │ │🏷️ feat│ │  │ │Feature │ │  │ │Page    │ │  │ │Docs    │ │              │
│ │ └───────┘ │  │ └────────┘ │  │ └────────┘ │  │ └────────┘ │              │
│ │    ...    │  │    ...     │  │    ...     │  │    ...     │              │
│ └───────────┘  └────────────┘  └────────────┘  └────────────┘              │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Task Card Component (Detail)
```
┌────────────────────┐
│ #142          🔴   │  ← Task ID + Priority indicator
│                    │
│ Implement User     │  ← Title (bold, 1rem)
│ Authentication     │
│                    │
│ Create JWT-based   │  ← Description (truncated, 0.875rem)
│ auth system with...│
│                    │
│ 🏷️ auth  🏷️ backend│  ← Labels/tags
│                    │
│ 👤 Sarah  📅 Sprint 4│ ← Assignee + Sprint
└────────────────────┘

States:
- Default: White background, subtle shadow
- Hover: Lift (transform), increased shadow
- Dragging: Opacity 0.5, larger shadow
- Selected: Blue border (2px)
```

### Column Header
```
┌─────────────────┐
│ BACKLOG    (12) │  ← Column name + count
│        [+]      │  ← Add task button
└─────────────────┘
```

### Empty Column State
```
┌─────────────────┐
│ BACKLOG    (0)  │
├─────────────────┤
│                 │
│     📋          │  ← Empty icon
│                 │
│  No tasks yet   │  ← Message
│                 │
│  [+ Add Task]   │  ← CTA button
│                 │
└─────────────────┘
```

---

## 4. Task Detail Modal

### Task Detail (View Mode)
```
┌────────────────────────────────────────────────────────────────────┐
│ Task #142                                           [Edit] [×]     │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│ Implement User Authentication                                     │
│ ──────────────────────────────────                                │
│                                                                    │
│ Status: Backlog                 Priority: High 🔴                 │
│ Created: 2h ago                 Updated: 1h ago                   │
│                                                                    │
│ ═══════════════════════════════════════════════════════════════   │
│                                                                    │
│ Description:                                                       │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ Create a JWT-based authentication system with:              │   │
│ │ - User registration                                         │   │
│ │ - Login/logout                                              │   │
│ │ - Password reset                                            │   │
│ │ - Session management                                        │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                                                                    │
│ Labels: 🏷️ auth  🏷️ backend  🏷️ security                        │
│                                                                    │
│ Assigned to: 👤 Sarah Johnson                                    │
│                                                                    │
│ Sprint: 📅 Sprint 4 - Q4 Goals                                   │
│                                                                    │
│ ═══════════════════════════════════════════════════════════════   │
│                                                                    │
│ Pipeline Status:                                                   │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ Not started                                                 │   │
│ │                                                             │   │
│ │ [▶️ Run Pipeline]                                           │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                                                                    │
│ ═══════════════════════════════════════════════════════════════   │
│                                                                    │
│ Activity:                                                          │
│ • Sarah created this task               2 hours ago               │
│ • John added label "security"           1 hour ago                │
│                                                                    │
│                                                                    │
│                                     [Delete Task]  [Close]         │
└────────────────────────────────────────────────────────────────────┘
```

### Create/Edit Task Modal
```
┌────────────────────────────────────────────────────────────────────┐
│ Create New Task                                              [×]   │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│ Title *                                                            │
│ <Enter task title...>                                             │
│                                                                    │
│ Description *                                                      │
│ ┌─────────────────────────────────────────────────────────────┐   │
│ │ Enter detailed description...                               │   │
│ │                                                             │   │
│ │                                                             │   │
│ │                                                             │   │
│ └─────────────────────────────────────────────────────────────┘   │
│                                                                    │
│ Priority                                                           │
│ ○ Low    ● Medium    ○ High                                       │
│                                                                    │
│ Labels                                                             │
│ [🏷️ auth] [🏷️ backend] [×]                                       │
│ <Add label...> ▼                                                  │
│                                                                    │
│ Assign to                                                          │
│ [Sarah Johnson ▼]                                                 │
│                                                                    │
│ Sprint (optional)                                                  │
│ [Sprint 4 - Q4 Goals ▼]                                           │
│                                                                    │
│                                                                    │
│                           [Cancel]  [Create Task]  [Create & Run] │
└────────────────────────────────────────────────────────────────────┘
```

---

## 5. Pipeline Monitoring

### Pipeline Status Page
```
┌────────────────────────────────────────────────────────────────────────────────┐
│ ← Back to Task #142                                                           │
│                                                                                │
│ Pipeline Execution - Task #142: Implement User Authentication                 │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│ ┌─Overview─────────────────────────────────────────────────────────────────┐  │
│ │                                                                          │  │
│ │  Status: 🟡 In Progress                                                 │  │
│ │  Started: 10 minutes ago                                                 │  │
│ │  Estimated time remaining: ~15 minutes                                   │  │
│ │                                                                          │  │
│ │  Overall Progress:                                                       │  │
│ │  ████████████████░░░░░░░░░░░░ 55%                                      │  │
│ │                                                                          │  │
│ │  Current Stage: Development                                              │  │
│ │                                                                          │  │
│ │  [⏸️ Pause]  [⏹️ Cancel]                                                │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│ ┌─Stages──────────────────────────────────────────────────────────────────┐  │
│ │                                                                          │  │
│ │ ✅ 1. Requirements Analysis                                             │  │
│ │    Completed in 2m 34s                                                   │  │
│ │    [View Artifacts] [View Logs]                                          │  │
│ │    ▼ Details                                                             │  │
│ │      • Generated requirements.yaml                                       │  │
│ │      • Extracted 12 user stories                                         │  │
│ │                                                                          │  │
│ │ ✅ 2. Architecture Design                                               │  │
│ │    Completed in 3m 12s                                                   │  │
│ │    [View Artifacts] [View Logs]                                          │  │
│ │                                                                          │  │
│ │ 🟡 3. Development                                                        │  │
│ │    In progress: 5m 23s                                                   │  │
│ │    ████████████░░░░░░░░ 60%                                             │  │
│ │    [View Logs]                                                           │  │
│ │    ▼ Details                                                             │  │
│ │      • Generating auth/models.py... ✅                                  │  │
│ │      • Generating auth/views.py... 🟡 (current)                         │  │
│ │      • Pending: auth/serializers.py                                      │  │
│ │      • Pending: auth/tests.py                                            │  │
│ │                                                                          │  │
│ │ ⏳ 4. Testing                                                            │  │
│ │    Waiting...                                                            │  │
│ │                                                                          │  │
│ │ ⏳ 5. Code Review                                                        │  │
│ │    Waiting...                                                            │  │
│ │                                                                          │  │
│ │ ⏳ 6. Documentation                                                      │  │
│ │    Waiting...                                                            │  │
│ │                                                                          │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│ ┌─Live Logs───────────────────────────────────────────────────────────────┐  │
│ │                                                                [Clear]   │  │
│ │ [2025-10-26 18:45:12] Starting development stage...                     │  │
│ │ [2025-10-26 18:45:15] Analyzing requirements...                         │  │
│ │ [2025-10-26 18:45:18] Generating auth/models.py...                      │  │
│ │ [2025-10-26 18:45:45] ✅ Created User model with fields:                │  │
│ │                          - username (CharField)                          │  │
│ │                          - email (EmailField)                            │  │
│ │                          - password_hash (CharField)                     │  │
│ │ [2025-10-26 18:46:02] Generating auth/views.py...                       │  │
│ │ [2025-10-26 18:46:15] Creating LoginView...                             │  │
│ │ ...                                                                      │  │
│ │                                                                          │  │
│ │ [📥 Download Logs] [⏸️ Auto-scroll: ON]                                │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Stage Icons Legend
```
✅ Completed (green)
🟡 In Progress (yellow)
⏳ Pending (gray)
❌ Failed (red)
⏭️ Skipped (gray)
```

---

## 6. Code Review

### Code Review Interface
```
┌────────────────────────────────────────────────────────────────────────────────┐
│ ← Back to Pipeline                                                            │
│                                                                                │
│ Code Review - Task #142: Implement User Authentication                        │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│ ┌─File Tree──┐ ┌─Code Viewer──────────────────────────────────────────────┐  │
│ │            │ │ auth/models.py                    [Original] [Generated]  │  │
│ │ 📁 auth    │ ├──────────────────────────────────────────────────────────┤  │
│ │  ├─📄 __i..│ │  1 │ from django.db import models                        │  │
│ │  ├─📄 mode..│ │  2 │ from django.contrib.auth.hashers import make..   │  │
│ │  ├─📄 view..│ │  3 │                                                     │  │
│ │  ├─📄 seri..│ │  4 │ class User(models.Model):                          │  │
│ │  ├─📄 urls..│ │  5 │     """User model with JWT authentication"""      │  │
│ │  └─📄 test..│ │  6 │     username = models.CharField(max_length=150,  │💬│
│ │            │ │  7 │                                  unique=True)       │  │
│ │ 📁 docs    │ │  8 │     email = models.EmailField(unique=True)         │  │
│ │  └─📄 API...│ │  9 │     password_hash = models.CharField(max_leng... │  │
│ │            │ │ 10 │     created_at = models.DateTimeField(auto_no... │  │
│ │ 📁 tests   │ │ 11 │     updated_at = models.DateTimeField(auto_no... │  │
│ │  └─📄 test..│ │ 12 │                                                     │  │
│ │            │ │ 13 │     def set_password(self, password):              │  │
│ │            │ │ 14 │         """Hash and set password"""                 │  │
│ │            │ │ 15 │         self.password_hash = make_password(pas... │  │
│ │ [Expand All│ │ 16 │                                                     │  │
│ │ Collapse...│ │ 17 │     def check_password(self, password):            │  │
│ └────────────┘ │ 18 │         """Verify password"""                       │  │
│                │ 19 │         return check_password(password, self.p... │  │
│                │ ... │ ...                                                 │  │
│                │     │                                                     │  │
│                └──────────────────────────────────────────────────────────┘  │
│                                                                                │
│ ┌─Comments (3)────────────────────────────────────────────────────────────┐  │
│ │                                                                          │  │
│ │ 💬 Line 6 - Sarah Johnson                                 2 min ago     │  │
│ │    Should we add email validation here?                                 │  │
│ │    [Reply] [Resolve]                                                     │  │
│ │                                                                          │  │
│ │ 💬 Line 13 - Mike Chen                                    5 min ago     │  │
│ │    Consider using Django's built-in user model instead                  │  │
│ │    [Reply] [Resolve]                                                     │  │
│ │      └─ RE: Sarah Johnson                                 3 min ago     │  │
│ │         Good point, but we need custom fields for JWT                   │  │
│ │                                                                          │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│ ┌─Review Actions──────────────────────────────────────────────────────────┐  │
│ │                                                                          │  │
│ │ <Add overall comment...>                                                │  │
│ │                                                                          │  │
│ │ [✅ Approve]  [⚠️ Request Changes]  [❌ Reject]          [Edit Code]    │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Diff View Mode
```
┌────────────────────────────────────────────────────────────────────────────────┐
│ auth/models.py                                      [Side-by-side] [Inline]   │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│ ┌─Original────────────────────────┐ ┌─Generated───────────────────────────┐  │
│ │  1 │ from django.db import mod...│ │  1 │ from django.db import mod...│  │
│ │  2 │                              │ │  2 │ from django.contrib.auth....│  │
│ │  3 │ class BasicUser(models.Mo...│ │  3 │                              │  │
│ │  4 │     username = models.Cha...│ │  4 │ class User(models.Model):   │  │
│ │  5 │     email = models.EmailF...│ │  5 │     """User model with JWT..│  │
│ │    │                              │ │  6 │     username = models.Cha...│  │
│ │    │                              │ │  7 │                  unique=T...│  │
│ │    │                              │ │  8 │     email = models.EmailF...│  │
│ │  6 │     def save(self, *args,...│ │  9 │     password_hash = models..│  │
│ │    │         super().save(*args...│ │ 10 │     created_at = models.D...│  │
│ │    │                              │ │ 11 │     updated_at = models.D...│  │
│ │    │                              │ │ 12 │                              │  │
│ │    │                              │ │ 13 │     def set_password(self...│  │
│ │    │                              │ │ 14 │         """Hash and set p...│  │
│ └─────────────────────────────────┘ └─────────────────────────────────────┘  │
│                                                                                │
│  Legend: ┃ Added (green bg)   ┃ Removed (red bg)   ┃ Modified (yellow bg)    │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Sprint Planning

### Sprint List Page
```
┌────────────────────────────────────────────────────────────────────────────────┐
│ Sprint Planning                                                 [+ New Sprint] │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│ ┌─Filters──────────────────────────────────────────────────────────────────┐  │
│ │ [Status: All ▼]  [Date Range ▼]  [Search...]                            │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│ ┌─Active Sprint───────────────────────────────────────────────────────────┐  │
│ │                                                                          │  │
│ │ 📅 Sprint 4 - Q4 Goals                                      [View Board] │  │
│ │                                                                          │  │
│ │ Oct 20, 2025 - Nov 3, 2025  (Day 7 of 14)                               │  │
│ │                                                                          │  │
│ │ Goal: Complete authentication and payment features                      │  │
│ │                                                                          │  │
│ │ Progress: ████████░░░░░░ 55%    (22/40 story points)                   │  │
│ │                                                                          │  │
│ │ ┌─Mini Stats─────────────────────────────────────────────────────────┐  │  │
│ │ │ 📊 12 tasks  |  ✅ 5 done  |  🟡 4 in progress  |  📋 3 todo       │  │  │
│ │ └────────────────────────────────────────────────────────────────────┘  │  │
│ │                                                                          │  │
│ │ [View Details]  [Close Sprint]                                           │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│ ┌─Upcoming Sprints─────────────────────────────────────────────────────────┐  │
│ │                                                                          │  │
│ │ 📅 Sprint 5 - Holiday Release                                           │  │
│ │ Nov 4, 2025 - Nov 18, 2025  (Planned)                                   │  │
│ │ 8 tasks planned  (32 story points)                                      │  │
│ │ [View] [Start Sprint]                                                    │  │
│ │                                                                          │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│ ┌─Past Sprints─────────────────────────────────────────────────────────────┐  │
│ │                                                                          │  │
│ │ ✅ Sprint 3 - UI Overhaul                                               │  │
│ │ Sep 23 - Oct 7, 2025  (Completed)                                       │  │
│ │ 16 tasks completed  (64/60 story points)  🎯 107% complete              │  │
│ │ Velocity: 4.3 pts/day                                                    │  │
│ │ [View Report]                                                            │  │
│ │                                                                          │  │
│ │ ✅ Sprint 2 - Core Features                                             │  │
│ │ Sep 9 - Sep 22, 2025  (Completed)                                       │  │
│ │ [View Report]                                                            │  │
│ │                                                                          │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Create Sprint Modal
```
┌──────────────────────────────────────────────────────────┐
│ Create New Sprint                                   [×]  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ Sprint Name *                                            │
│ <Sprint 5 - Holiday Release>                            │
│                                                          │
│ Start Date *                  End Date *                 │
│ [Nov 4, 2025   ▼]            [Nov 18, 2025  ▼]         │
│                                                          │
│ Duration: 14 days                                        │
│                                                          │
│ Sprint Goal *                                            │
│ ┌────────────────────────────────────────────────────┐  │
│ │ Prepare holiday features and bug fixes            │  │
│ │                                                    │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│ Story Point Capacity (optional)                          │
│ <40>                                                     │
│                                                          │
│                                                          │
│                          [Cancel]  [Create Sprint]       │
└──────────────────────────────────────────────────────────┘
```

---

## 8. Sprint Detail

### Sprint Detail Page
```
┌────────────────────────────────────────────────────────────────────────────────┐
│ ← Back to Sprints                                                             │
│                                                                                │
│ Sprint 4 - Q4 Goals                          [Edit] [Close Sprint] [Settings] │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│ ┌─Sprint Overview──────────────────────────────────────────────────────────┐  │
│ │                                                                          │  │
│ │ 📅 Oct 20, 2025 - Nov 3, 2025                Status: 🟢 Active          │  │
│ │                                                                          │  │
│ │ Day 7 of 14  ████████░░░░░░░░░░░░░░░░ 50%                             │  │
│ │                                                                          │  │
│ │ Goal: Complete authentication and payment features                      │  │
│ │                                                                          │  │
│ │ ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                │  │
│ │ │   40     │  │   22     │  │  55%     │  │  3.1     │                │  │
│ │ │ Total    │  │ Completed│  │ Progress │  │ Velocity │                │  │
│ │ │ Points   │  │ Points   │  │          │  │ pts/day  │                │  │
│ │ └──────────┘  └──────────┘  └──────────┘  └──────────┘                │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│ ┌─Tabs─────────────────────────────────────────────────────────────────────┐  │
│ │ [Backlog] [Board] [Burndown] [Metrics]                                  │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│ ┌─Sprint Backlog───────────────────────────────────────────────────────────┐  │
│ │                                                                          │  │
│ │ ┌─Available Tasks (Drag to Sprint)─────┐  ┌─Sprint Tasks───────────┐   │  │
│ │ │                                       │  │                         │   │  │
│ │ │ 🔵 #145 - Email notifications         │  │ ✅ #142 - Auth system  │   │  │
│ │ │    5 pts                              │  │    8 pts               │   │  │
│ │ │                                       │  │                         │   │  │
│ │ │ 🔵 #146 - Search functionality        │  │ 🟡 #139 - Payment API  │   │  │
│ │ │    8 pts                              │  │    13 pts              │   │  │
│ │ │                                       │  │                         │   │  │
│ │ │ 🔵 #147 - Dashboard widgets           │  │ 🟡 #138 - Search       │   │  │
│ │ │    5 pts                              │  │    5 pts               │   │  │
│ │ │                                       │  │                         │   │  │
│ │ │ ...                                   │  │ 📋 #137 - Dashboard UI │   │  │
│ │ │                                       │  │    8 pts               │   │  │
│ │ │                                       │  │                         │   │  │
│ │ │                                       │  │ ...                     │   │  │
│ │ │                                       │  │                         │   │  │
│ │ │                                       │  │ Total: 40 pts          │   │  │
│ │ └───────────────────────────────────────┘  └─────────────────────────┘   │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Burndown Chart Tab
```
┌────────────────────────────────────────────────────────────────────────────────┐
│ Burndown Chart                                                                 │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│ ┌──────────────────────────────────────────────────────────────────────────┐  │
│ │ Story                                                                    │  │
│ │ Points                                                                   │  │
│ │  40 ─                                                                    │  │
│ │     │●                                                                   │  │
│ │  35 ─│ ●                                                                 │  │
│ │     │   ●                                                                │  │
│ │  30 ─│     ○                                                             │  │
│ │     │       ○    Ideal ─ ─ ─ ─ ─ ─                                      │  │
│ │  25 ─│         ○  ○                                                      │  │
│ │     │             ○      Actual ●●●●●                                    │  │
│ │  20 ─│               ○                                                   │  │
│ │     │                 ○                                                  │  │
│ │  15 ─│                   ○                                               │  │
│ │     │                     ○                                              │  │
│ │  10 ─│                       ○                                           │  │
│ │     │                         ○                                          │  │
│ │   5 ─│                           ○                                       │  │
│ │     │                             ○                                      │  │
│ │   0 ─┴─────┴─────┴─────┴─────┴─────┴─────┴─────                         │  │
│ │     D1    D3    D5    D7    D9   D11   D13  D14                         │  │
│ │                            Days                                          │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│ ┌─Insights─────────────────────────────────────────────────────────────────┐  │
│ │ • On track: Current pace matches ideal burndown                         │  │
│ │ • 7 days remaining                                                       │  │
│ │ • At current velocity, sprint will complete with 2 pts remaining        │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. RAG Knowledge Browser

### RAG Knowledge Page
```
┌────────────────────────────────────────────────────────────────────────────────┐
│ Knowledge Base                                                [Upload Document]│
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│ ┌─Search───────────────────────────────────────────────────────────────────┐  │
│ │ 🔍 Search knowledge base...                                    [Advanced]│  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│ ┌─Filters──────────────────────────────────────────────────────────────────┐  │
│ │ Source: [All ▼]  Type: [All ▼]  Language: [All ▼]  [Clear Filters]     │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│ ┌─Categories───────────────────────────────────────────────────────────────┐  │
│ │                                                                          │  │
│ │ ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │  │
│ │ │   📚     │  │   ⚛️     │  │   🐍     │  │   🎨     │  │   🔧     │  │  │
│ │ │  Books   │  │  React   │  │  Django  │  │  UI/UX   │  │  Tools   │  │  │
│ │ │  (342)   │  │  (156)   │  │  (189)   │  │  (78)    │  │  (45)    │  │  │
│ │ └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│ ┌─Recent Uploads───────────────────────────────────────────────────────────┐  │
│ │                                                                          │  │
│ │ 📄 React 18 Design Patterns                            2 hours ago      │  │
│ │    PDF • 495 chunks • Web Development                                   │  │
│ │    [View] [Search within]                                               │  │
│ │                                                                          │  │
│ │ 📄 Django 5 Cookbook                                   1 day ago        │  │
│ │    PDF • 287 chunks • Backend Development                               │  │
│ │    [View] [Search within]                                               │  │
│ │                                                                          │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│ ┌─Search Results (showing 1-10 of 45)──────────────────────────────────────┐  │
│ │                                                                          │  │
│ │ 1. Django Authentication Best Practices                    Relevance: 95%│  │
│ │    Source: Django 5 Cookbook • Chapter 8                                │  │
│ │    "Implementing JWT-based authentication in Django requires..."        │  │
│ │    [View Full] [Add to Task]                                            │  │
│ │                                                                          │  │
│ │ 2. React Form Validation Patterns                         Relevance: 87%│  │
│ │    Source: React 18 Design Patterns • Chapter 12                        │  │
│ │    "Modern React applications use controlled components for..."         │  │
│ │    [View Full] [Add to Task]                                            │  │
│ │                                                                          │  │
│ │ 3. User Authentication Flow Diagram                       Relevance: 82%│  │
│ │    Source: Full Stack React • Page 145                                  │  │
│ │    "The authentication flow begins with the login form..."              │  │
│ │    [View Full] [Add to Task]                                            │  │
│ │                                                                          │  │
│ │ ...                                                                      │  │
│ │                                                                          │  │
│ │ [Load More]                                                              │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Document Viewer Modal
```
┌────────────────────────────────────────────────────────────────────┐
│ Django Authentication Best Practices                          [×]  │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│ Source: Django 5 Cookbook • Chapter 8 • Pages 145-150             │
│ Added: 1 day ago                                                   │
│                                                                    │
│ ═══════════════════════════════════════════════════════════════   │
│                                                                    │
│ ┌──────────────────────────────────────────────────────────────┐  │
│ │ Implementing JWT-Based Authentication in Django              │  │
│ │                                                              │  │
│ │ JSON Web Tokens (JWT) provide a stateless authentication    │  │
│ │ mechanism that's ideal for modern web applications...       │  │
│ │                                                              │  │
│ │ Installation:                                                │  │
│ │ ```bash                                                      │  │
│ │ pip install djangorestframework-simplejwt                    │  │
│ │ ```                                                          │  │
│ │                                                              │  │
│ │ Configuration in settings.py:                                │  │
│ │ ```python                                                    │  │
│ │ REST_FRAMEWORK = {                                           │  │
│ │     'DEFAULT_AUTHENTICATION_CLASSES': [                      │  │
│ │         'rest_framework_simplejwt.authentication.JWT...      │  │
│ │     ],                                                       │  │
│ │ }                                                            │  │
│ │ ```                                                          │  │
│ │                                                              │  │
│ │ ...                                                          │  │
│ │                                                              │  │
│ └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│                                          [Copy] [Download] [Close] │
└────────────────────────────────────────────────────────────────────┘
```

### Upload Document Interface
```
┌────────────────────────────────────────────────────────────────────┐
│ Upload Document to Knowledge Base                            [×]  │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│ ┌──────────────────────────────────────────────────────────────┐  │
│ │                                                              │  │
│ │               Drag & drop files here                         │  │
│ │                      or                                      │  │
│ │                [Browse Files]                                │  │
│ │                                                              │  │
│ │  Supported: PDF, EPUB, TXT, MD (max 50MB each)              │  │
│ │                                                              │  │
│ └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│ ┌─Upload Queue─────────────────────────────────────────────────┐  │
│ │                                                              │  │
│ │ 📄 react-patterns.pdf                                        │  │
│ │    ████████████████████░░ 85% (4.2 MB / 5.0 MB)            │  │
│ │                                                              │  │
│ │ 📄 django-guide.epub                                         │  │
│ │    ⏳ Waiting...                                            │  │
│ │                                                              │  │
│ └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│ Settings:                                                          │
│ ☑ Extract text automatically                                      │
│ ☑ Generate embeddings                                             │
│ ☑ Enable semantic search                                          │
│                                                                    │
│                                     [Cancel]  [Start Upload]       │
└────────────────────────────────────────────────────────────────────┘
```

---

## 10. Settings Pages

### Settings Layout
```
┌────────────────────────────────────────────────────────────────────────────────┐
│ Settings                                                                       │
├──────────────┬─────────────────────────────────────────────────────────────────┤
│              │                                                                 │
│ ┌─Nav─────┐ │                                                                 │
│ │ General │ │  GENERAL SETTINGS                                               │
│ │ LLM Config ├─────────────────────────────────────────────────────────────┐  │
│ │ Git     │ │                                                              │  │
│ │ Pipeline│ │  Application Name                                            │  │
│ │ Notif.. │ │  <Artemis>                                                   │  │
│ │ Users   │ │                                                              │  │
│ │ Advanced│ │  Timezone                                                    │  │
│ └─────────┘ │  [America/Los_Angeles ▼]                                    │  │
│              │                                                              │  │
│              │  Default Project Settings                                   │  │
│              │  ☑ Auto-run pipeline on task creation                       │  │
│              │  ☑ Auto-commit code reviews                                 │  │
│              │  ☐ Require approval for all code                            │  │
│              │                                                              │  │
│              │  Language & Region                                          │  │
│              │  Language: [English ▼]                                      │  │
│              │  Date Format: [MM/DD/YYYY ▼]                                │  │
│              │                                                              │  │
│              │                                                              │  │
│              │                                    [Cancel]  [Save Changes]  │  │
│              └──────────────────────────────────────────────────────────────┘  │
└──────────────┴─────────────────────────────────────────────────────────────────┘
```

### LLM Configuration Tab
```
┌──────────────────────────────────────────────────────────────────────────────┐
│ LLM CONFIGURATION                                                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Provider                                                                     │
│ ● OpenAI    ○ Anthropic                                                     │
│                                                                              │
│ ═══════════════════════════════════════════════════════════════             │
│                                                                              │
│ OpenAI Settings                                                              │
│                                                                              │
│ API Key *                                                                    │
│ <sk-************************************************> [👁️ Show]             │
│ [Test Connection]                                                            │
│                                                                              │
│ Model                                                                        │
│ [gpt-4-turbo-preview ▼]                                                     │
│                                                                              │
│ Temperature: 0.7  ├────●────────┤  1.0                                      │
│                                                                              │
│ Max Tokens per Request                                                       │
│ <4000>                                                                       │
│                                                                              │
│ Rate Limiting                                                                │
│ ☑ Enable rate limiting                                                      │
│ Max requests per minute: <60>                                               │
│                                                                              │
│ Cost Controls                                                                │
│ ☑ Enable cost tracking                                                      │
│ Monthly budget: $<500.00>                                                   │
│ Alert when: [80%] of budget used                                            │
│                                                                              │
│ Current Usage This Month:                                                    │
│ ████████░░░░░░ $234.56 / $500.00 (47%)                                     │
│                                                                              │
│                                                                              │
│                                           [Cancel]  [Test & Save]            │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Git Integration Tab
```
┌──────────────────────────────────────────────────────────────────────────────┐
│ GIT INTEGRATION                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Repository URL *                                                             │
│ <https://github.com/myorg/myproject.git>                                    │
│                                                                              │
│ Default Branch                                                               │
│ <main>                                                                       │
│                                                                              │
│ Authentication Method                                                        │
│ ● HTTPS (Personal Access Token)    ○ SSH Key                                │
│                                                                              │
│ Personal Access Token *                                                      │
│ <ghp_************************************************> [👁️ Show]           │
│                                                                              │
│ [Test Connection]   Status: ✅ Connected                                    │
│                                                                              │
│ ═══════════════════════════════════════════════════════════════             │
│                                                                              │
│ Commit Settings                                                              │
│                                                                              │
│ Commit Message Template                                                      │
│ ┌────────────────────────────────────────────────────────────────────────┐  │
│ │ feat: {{task_title}}                                                   │  │
│ │                                                                        │  │
│ │ {{task_description}}                                                   │  │
│ │                                                                        │  │
│ │ Generated by Artemis                                                   │  │
│ │ Task ID: {{task_id}}                                                   │  │
│ └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│ Auto-commit Settings                                                         │
│ ☑ Auto-commit approved code reviews                                         │
│ ☑ Create feature branches for each task                                     │
│ ☐ Auto-create pull requests                                                 │
│                                                                              │
│ Branch Naming Pattern                                                        │
│ <feature/{{task_id}}-{{slug}}>                                              │
│                                                                              │
│                                                                              │
│                                           [Cancel]  [Save Changes]           │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. Mobile Views

### Mobile Dashboard (375px width)
```
┌─────────────────────────────────────┐
│ ☰  ARTEMIS          [🔔] [User ▼] │
├─────────────────────────────────────┤
│                                     │
│ ┌─Quick Stats────────────────────┐ │
│ │ ┌────────┐  ┌────────┐         │ │
│ │ │  24    │  │  12    │         │ │
│ │ │Active  │  │ This   │         │ │
│ │ │Tasks   │  │ Week   │         │ │
│ │ └────────┘  └────────┘         │ │
│ │ ┌────────┐  ┌────────┐         │ │
│ │ │  87%   │  │   6    │         │ │
│ │ │Success │  │ Sprint │         │ │
│ │ │Rate    │  │Progress│         │ │
│ │ └────────┘  └────────┘         │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─Recent Tasks────────────────────┐ │
│ │                                 │ │
│ │ 🔵 #142 - Implement auth        │ │
│ │    2h ago                       │ │
│ │    [View] [Run]                 │ │
│ │                                 │ │
│ │ 🟢 #141 - Fix login             │ │
│ │    5h ago                       │ │
│ │    [View] [Run]                 │ │
│ │                                 │ │
│ │ [View All]                      │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─Active Pipelines────────────────┐ │
│ │                                 │ │
│ │ 🟡 #142 - In Progress          │ │
│ │    Development (60%)            │ │
│ │    [View]                       │ │
│ │                                 │ │
│ └─────────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

### Mobile Kanban Board
```
┌─────────────────────────────────────┐
│ ← Kanban      [Filter] [+ Task]    │
├─────────────────────────────────────┤
│                                     │
│ Swipe left/right for columns ←→    │
│                                     │
│ ┌─BACKLOG (12)────────────────────┐ │
│ │                                 │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ #142                   🔴   │ │ │
│ │ │                             │ │ │
│ │ │ Implement User Auth         │ │ │
│ │ │                             │ │ │
│ │ │ 🏷️ auth  🏷️ backend         │ │ │
│ │ │                             │ │ │
│ │ │ 👤 Sarah                    │ │ │
│ │ └─────────────────────────────┘ │ │
│ │                                 │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ #141                        │ │ │
│ │ │ Email Notifications         │ │ │
│ │ │ 🏷️ feature                  │ │ │
│ │ │ 👤 Mike                     │ │ │
│ │ └─────────────────────────────┘ │ │
│ │                                 │ │
│ │ ...                             │ │
│ │                                 │ │
│ │ [Load More]                     │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ● BACKLOG   ○ IN PROGRESS          │
│ ○ REVIEW    ○ DONE                 │
└─────────────────────────────────────┘
```

### Mobile Pipeline Monitoring
```
┌─────────────────────────────────────┐
│ ← Pipeline #142                     │
├─────────────────────────────────────┤
│                                     │
│ ┌─Status───────────────────────────┐ │
│ │ 🟡 In Progress                   │ │
│ │                                  │ │
│ │ Overall Progress:                │ │
│ │ ████████░░░░ 55%                │ │
│ │                                  │ │
│ │ Est. ~15min remaining            │ │
│ │                                  │ │
│ │ [⏸️ Pause] [⏹️ Cancel]          │ │
│ └──────────────────────────────────┘ │
│                                     │
│ ┌─Stages──────────────────────────┐ │
│ │                                 │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ ✅ Requirements             │ │ │
│ │ │ Completed in 2m 34s         │ │ │
│ │ │ [View]                      │ │ │
│ │ └─────────────────────────────┘ │ │
│ │                                 │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ ✅ Architecture             │ │ │
│ │ │ Completed in 3m 12s         │ │ │
│ │ │ [View]                      │ │ │
│ │ └─────────────────────────────┘ │ │
│ │                                 │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ 🟡 Development              │ │ │
│ │ │ ████████░░░░ 60%           │ │ │
│ │ │ Running 5m 23s              │ │ │
│ │ │ [View Logs]                 │ │ │
│ │ └─────────────────────────────┘ │ │
│ │                                 │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ ⏳ Testing                  │ │ │
│ │ │ Waiting...                  │ │ │
│ │ └─────────────────────────────┘ │ │
│ │                                 │ │
│ │ ...                             │ │
│ └─────────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

### Mobile Navigation Menu (Drawer)
```
┌─────────────────────────────────────┐
│                                [×]  │
│                                     │
│ ┌─User───────────────────────────┐ │
│ │ 👤 Sarah Johnson               │ │
│ │ sarah@example.com              │ │
│ └─────────────────────────────────┘ │
│                                     │
│ 🏠 Dashboard                        │
│                                     │
│ 📋 Kanban Board                     │
│                                     │
│ 📅 Sprints                          │
│                                     │
│ 📚 Knowledge Base                   │
│                                     │
│ ⚙  Settings                         │
│                                     │
│ ═══════════════════════════════════ │
│                                     │
│ 📊 Usage Stats                      │
│                                     │
│ 💡 Help & Support                   │
│                                     │
│ 🚪 Logout                           │
│                                     │
└─────────────────────────────────────┘
```

---

## 12. Component States

### Button States
```
┌─────────────┐
│  [Primary]  │  ← Default (blue, white text)
└─────────────┘

┌─────────────┐
│  [Primary]  │  ← Hover (darker blue, scale 1.02)
└─────────────┘

┌─────────────┐
│  [Primary]  │  ← Active/Pressed (darkest blue, scale 0.98)
└─────────────┘

┌─────────────┐
│  [Primary]  │  ← Disabled (gray, opacity 0.5, no pointer)
└─────────────┘

┌─────────────┐
│  ⏳ Loading │  ← Loading state (spinner)
└─────────────┘
```

### Card States
```
┌──────────────┐
│  Card        │  ← Default (white, subtle shadow)
│              │
└──────────────┘

┌──────────────┐
│  Card        │  ← Hover (lift, stronger shadow)
│              │
└──────────────┘

┌──────────────┐
│  Card        │  ← Selected (blue border, 2px)
│              │
└──────────────┘

┌──────────────┐
│  Card        │  ← Dragging (opacity 0.5)
│              │
└──────────────┘
```

### Input States
```
<Input placeholder>         ← Default (gray border)

<Input placeholder>         ← Focus (blue border, shadow)

<Input with value>          ← Filled

<Input placeholder>         ← Error (red border)
⚠️ Error message here

<Input placeholder>         ← Disabled (gray bg, no pointer)
```

### Empty States
```
┌────────────────────────────────────┐
│                                    │
│              📋                    │  ← Icon
│                                    │
│        No tasks yet                │  ← Message
│                                    │
│    Get started by creating         │  ← Description
│    your first task                 │
│                                    │
│       [+ Create Task]              │  ← CTA
│                                    │
└────────────────────────────────────┘
```

### Loading States
```
Skeleton Screen:
┌──────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓░░░░░░░               │  ← Animated gradient
│ ▓▓▓▓▓▓░░░░░░░░░░░░░░░░         │
│                                  │
│ ▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░            │
│ ▓▓▓▓░░░░░░░░░░░░░░░░░░         │
└──────────────────────────────────┘

Spinner:
      ○○○○●
     ○    ●
     ○    ●
     ●    ○
      ●●○○○

Progress Bar:
████████░░░░░░░░ 45%
```

---

## Design Notes

### 1. Consistency
- All wireframes use the same spacing (8px grid)
- Color coding consistent across pages
- Icons from same icon family (Lucide)
- Typography hierarchy maintained

### 2. Accessibility
- Touch targets minimum 44x44px on mobile
- Clear focus indicators for keyboard nav
- High contrast text (4.5:1 ratio minimum)
- Alt text for all icons and images

### 3. Responsive Behavior
- Mobile: Single column, stacked
- Tablet: 2 columns where appropriate
- Desktop: Full multi-column layouts
- Sidebar collapses on smaller screens

### 4. Interactions
- All buttons have hover/active states
- Cards lift on hover
- Smooth transitions (200-300ms)
- Loading states for all async operations

### 5. Color Coding
- 🔵 Blue: Info/neutral
- 🟢 Green: Success/completed
- 🟡 Yellow: In progress/warning
- 🔴 Red: Error/failed/high priority
- ⚫ Gray: Disabled/pending

---

## Appendix: Component Library Reference

### Buttons
- Primary: Blue background, white text
- Secondary: White background, blue border
- Ghost: Transparent, blue text
- Destructive: Red background, white text
- Link: No background, underlined

### Cards
- Default: White, rounded 8px, shadow-sm
- Hover: shadow-md, lift 2px
- Selected: Blue border 2px

### Modals
- Centered overlay
- Dark backdrop (opacity 0.5)
- Max width: 600px (forms), 1200px (viewers)
- Padding: 24px

### Forms
- Label above input
- Required fields marked with *
- Validation messages inline
- Submit buttons right-aligned

---

**Document Control:**
- Author: Claude (AI Assistant)
- Review Status: Draft
- Next Review: Before implementation begins
