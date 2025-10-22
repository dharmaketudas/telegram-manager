# Design Document

## Overview

The Telegram Contact Management system is a Python-based application that leverages the Telegram Client API (via Telethon library) to discover, organize, and communicate with contacts across all Telegram chats. The system provides a comprehensive contact management interface with tagging capabilities and bulk messaging features.

### Technology Stack

**Backend**:
- **Language**: Python 3.9+
- **Web Framework**: FastAPI (async, modern, auto-documentation)
- **Telegram API Client**: Telethon (mature, asynchronous, well-documented)
- **Database**: SQLite (embedded, lightweight, suitable for local data)
- **Configuration Management**: python-dotenv for environment variables
- **Image Handling**: Pillow for profile image processing
- **Async Framework**: asyncio for concurrent operations
- **CORS Middleware**: fastapi-cors for cross-origin requests

**Frontend**:
- **Framework**: React 18+
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI) or Tailwind CSS
- **State Management**: React Query for server state, Zustand for client state
- **HTTP Client**: Axios
- **Image Display**: React components with lazy loading
- **Routing**: React Router

### Design Principles

1. **Separation of Concerns**: Clear boundaries between Telegram API interaction, business logic, data persistence, and presentation
2. **Asynchronous Operations**: Leverage async/await for efficient I/O operations with Telegram API
3. **Modularity**: Independent, testable components with well-defined interfaces
4. **Data Integrity**: Consistent state management with transactional database operations
5. **Resilience**: Graceful error handling with retry logic for network operations

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (React SPA)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Contact List │  │ Contact View │  │  Tag Manager │     │
│  │  Component   │  │  Component   │  │  Component   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Messaging  │  │     Auth     │  │    Media     │     │
│  │  Component   │  │  Component   │  │   Display    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP/REST API
┌────────────────────────────┼────────────────────────────────┐
│                  API Layer (FastAPI)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Contact    │  │     Tag      │  │   Messaging  │     │
│  │  Endpoints   │  │  Endpoints   │  │  Endpoints   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │     Auth     │  │     Sync     │  │    Media     │     │
│  │  Endpoints   │  │  Endpoints   │  │  Endpoints   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────┐
│                     Service Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Contact    │  │     Tag      │  │   Messaging  │     │
│  │   Service    │  │   Service    │  │   Service    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │     Sync     │  │     Auth     │                        │
│  │   Service    │  │   Service    │                        │
│  └──────────────┘  └──────────────┘                        │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────┐
│                   Data Access Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Contact    │  │     Tag      │  │   Message    │     │
│  │ Repository   │  │ Repository   │  │ Repository   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │    Group     │  │   Session    │                        │
│  │ Repository   │  │   Manager    │                        │
│  └──────────────┘  └──────────────┘                        │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────┐
│                  Integration Layer                           │
│  ┌──────────────────────────────────────────────┐           │
│  │          Telegram Client Wrapper             │           │
│  │            (Telethon Adapter)                │           │
│  └──────────────────────────────────────────────┘           │
└────────────────────────────┬────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │  Telegram API   │
                    └─────────────────┘
```

### Layer Responsibilities

#### Frontend Layer (React)
- Render interactive UI components
- Handle user interactions and form submissions
- Manage client-side state and navigation
- Display images, profile photos, and rich media
- Provide real-time feedback and loading states

#### API Layer (FastAPI)
- Expose RESTful endpoints for frontend consumption
- Handle HTTP request/response cycles
- Validate incoming requests
- Serialize/deserialize data to/from JSON
- Serve static media files (profile photos)
- Handle authentication and session management
- Provide WebSocket endpoints for real-time updates (optional)

#### Service Layer
- Implement business logic independent of presentation
- Coordinate between repositories and Telegram client
- Handle complex operations (contact discovery, bulk messaging)
- Apply business rules and validation
- Process and transform data for API consumption

#### Data Access Layer
- Provide CRUD operations for all entities
- Manage database connections and transactions
- Handle data mapping between domain models and database records
- Ensure data consistency

#### Integration Layer
- Wrap Telegram API client (Telethon)
- Provide simplified, domain-specific methods
- Handle authentication and session management
- Implement rate limiting and retry logic

## Components and Interfaces

### 1. REST API Endpoints (FastAPI)

**Purpose**: Expose backend functionality to the frontend via HTTP

**Contact Endpoints**:
```python
# GET /api/contacts - List all contacts with optional filtering
# GET /api/contacts/{contact_id} - Get contact details
# GET /api/contacts/{contact_id}/profile - Get full contact profile
# POST /api/contacts/sync - Trigger contact synchronization
# GET /api/contacts/search?q={query} - Search contacts

@router.get("/api/contacts")
async def list_contacts(
    skip: int = 0,
    limit: int = 50,
    search: str = None,
    tag_id: int = None
) -> List[ContactResponse]

@router.get("/api/contacts/{contact_id}/profile")
async def get_contact_profile(contact_id: int) -> ContactProfileResponse
```

**Tag Endpoints**:
```python
# GET /api/tags - List all tags
# POST /api/tags - Create new tag
# PUT /api/tags/{tag_id} - Update tag
# DELETE /api/tags/{tag_id} - Delete tag
# POST /api/contacts/{contact_id}/tags - Add tag to contact
# DELETE /api/contacts/{contact_id}/tags/{tag_id} - Remove tag from contact

@router.post("/api/tags")
async def create_tag(tag: TagCreate) -> TagResponse

@router.post("/api/contacts/{contact_id}/tags")
async def add_tag_to_contact(contact_id: int, tag_id: int) -> bool
```

**Messaging Endpoints**:
```python
# POST /api/messages/send - Send message to single contact
# POST /api/messages/bulk - Send bulk message by tags
# GET /api/messages/status/{job_id} - Get bulk message status

@router.post("/api/messages/send")
async def send_message(request: SendMessageRequest) -> MessageResult

@router.post("/api/messages/bulk")
async def send_bulk_message(request: BulkMessageRequest) -> BulkMessageJob
```

**Authentication Endpoints**:
```python
# POST /api/auth/init - Initialize authentication
# POST /api/auth/code - Submit verification code
# POST /api/auth/password - Submit 2FA password
# GET /api/auth/status - Check authentication status
# POST /api/auth/logout - Logout

@router.post("/api/auth/init")
async def init_auth(request: AuthInitRequest) -> AuthResponse

@router.get("/api/auth/status")
async def get_auth_status() -> AuthStatusResponse
```

**Media Endpoints**:
```python
# GET /api/media/profile-photos/{filename} - Serve profile photos
# GET /api/media/group-photos/{filename} - Serve group photos

@router.get("/api/media/profile-photos/{filename}")
async def get_profile_photo(filename: str) -> FileResponse
```

**Sync Endpoints**:
```python
# POST /api/sync/contacts - Sync contacts
# POST /api/sync/messages - Sync messages
# GET /api/sync/status - Get sync status

@router.post("/api/sync/contacts")
async def sync_contacts() -> SyncJobResponse
```

### 2. API Response Schemas (Pydantic)

**Purpose**: Define data contracts between backend and frontend

**Contact Schemas**:
```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ContactResponse(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    display_name: str
    phone: Optional[str]
    profile_photo_url: Optional[str]
    tags: List[str]
    updated_at: datetime
    
    class Config:
        orm_mode = True

class GroupInfo(BaseModel):
    id: int
    telegram_id: int
    name: str
    member_count: int
    profile_photo_url: Optional[str]

class MessageInfo(BaseModel):
    id: int
    content: Optional[str]
    timestamp: datetime
    is_outgoing: bool

class ContactProfileResponse(BaseModel):
    contact: ContactResponse
    tags: List[TagResponse]
    mutual_groups: List[GroupInfo]
    last_received_message: Optional[MessageInfo]
    last_sent_message: Optional[MessageInfo]
```

**Tag Schemas**:
```python
class TagCreate(BaseModel):
    name: str
    color: Optional[str] = None

class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

class TagResponse(BaseModel):
    id: int
    name: str
    color: Optional[str]
    created_at: datetime
    contact_count: int
    
    class Config:
        orm_mode = True
```

**Message Schemas**:
```python
class SendMessageRequest(BaseModel):
    contact_id: int
    message: str

class BulkMessageRequest(BaseModel):
    tag_ids: List[int]
    message: str

class MessageResult(BaseModel):
    success: bool
    message_id: Optional[int]
    error: Optional[str]

class BulkMessageJob(BaseModel):
    job_id: str
    total_contacts: int
    status: str  # 'pending', 'in_progress', 'completed'

class BulkMessageStatus(BaseModel):
    job_id: str
    total_contacts: int
    sent: int
    failed: int
    in_progress: bool
    failures: List[dict]
```

**Auth Schemas**:
```python
class AuthInitRequest(BaseModel):
    api_id: int
    api_hash: str
    phone: str

class AuthCodeRequest(BaseModel):
    phone: str
    code: str

class AuthPasswordRequest(BaseModel):
    password: str

class AuthResponse(BaseModel):
    success: bool
    requires_code: bool = False
    requires_password: bool = False
    message: str

class AuthStatusResponse(BaseModel):
    authenticated: bool
    phone: Optional[str]
    session_valid: bool
```

**Sync Schemas**:
```python
class SyncJobResponse(BaseModel):
    job_id: str
    sync_type: str
    status: str
    started_at: datetime

class SyncStatusResponse(BaseModel):
    job_id: str
    status: str
    records_processed: int
    completed_at: Optional[datetime]
```

### 3. Frontend Components (React)

**Purpose**: Interactive UI components for rich user experience with image display

**ContactList Component**:
```typescript
interface ContactListProps {
    contacts: Contact[];
    onContactClick: (contactId: number) => void;
    selectedTags: number[];
    searchQuery: string;
}

// Features:
// - Virtual scrolling for large lists
// - Profile photo thumbnails
// - Tag badges display
// - Search and filter integration
// - Loading states and skeletons
```

**ContactProfile Component**:
```typescript
interface ContactProfileProps {
    contactId: number;
}

// Features:
// - Large profile photo display with fallback
// - Contact information display
// - Tag management (add/remove)
// - Mutual groups grid with group photos
// - Last messages display with timestamps
// - Send message quick action
```

**ProfileImage Component**:
```typescript
interface ProfileImageProps {
    imageUrl?: string;
    alt: string;
    size: 'small' | 'medium' | 'large';
    fallback?: string;
}

// Features:
// - Lazy loading with intersection observer
// - Placeholder while loading
// - Fallback to initials or default avatar
// - Circular or square variants
// - Error handling for broken images
```

**TagManager Component**:
```typescript
interface TagManagerProps {
    contactId?: number;
    tags: Tag[];
    assignedTags: number[];
    onTagAdd: (tagId: number) => void;
    onTagRemove: (tagId: number) => void;
}

// Features:
// - Create new tags inline
// - Color picker for tags
// - Autocomplete for existing tags
// - Visual tag chips with colors
// - Bulk tag operations
```

**BulkMessageDialog Component**:
```typescript
interface BulkMessageDialogProps {
    open: boolean;
    onClose: () => void;
    tags: Tag[];
}

// Features:
// - Multi-tag selection
// - Preview contact list with photos
// - Message composition with character count
// - Send progress tracking
// - Results summary with retry option
```

**GroupList Component**:
```typescript
interface GroupListProps {
    groups: Group[];
    compact?: boolean;
}

// Features:
// - Grid or list view toggle
// - Group photo display
// - Member count badges
// - Clickable group names
// - Empty state message
```

**MessageComposer Component**:
```typescript
interface MessageComposerProps {
    onSend: (message: string) => void;
    placeholder?: string;
    maxLength?: number;
}

// Features:
// - Multi-line text input
// - Character counter
// - Send button with loading state
// - Message preview
// - Keyboard shortcuts
```

**SearchBar Component**:
```typescript
interface SearchBarProps {
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
}

// Features:
// - Debounced search input
// - Clear button
// - Search suggestions
// - Recent searches
// - Keyboard navigation
```

### 4. Frontend State Management

**React Query Hooks**:
```typescript
// Custom hooks for data fetching
function useContacts(filters?: ContactFilters) {
    return useQuery(['contacts', filters], () => 
        api.getContacts(filters)
    );
}

function useContactProfile(contactId: number) {
    return useQuery(['contact', contactId], () =>
        api.getContactProfile(contactId)
    );
}

function useTags() {
    return useQuery(['tags'], () => api.getTags());
}

// Mutations
function useAddTag() {
    const queryClient = useQueryClient();
    return useMutation(
        (data: { contactId: number; tagId: number }) =>
            api.addTagToContact(data.contactId, data.tagId),
        {
            onSuccess: () => {
                queryClient.invalidateQueries(['contacts']);
            }
        }
    );
}

function useSendBulkMessage() {
    return useMutation(
        (data: BulkMessageRequest) => api.sendBulkMessage(data)
    );
}
```

**Zustand Store for Client State**:
```typescript
interface AppState {
    // Auth state
    isAuthenticated: boolean;
    setAuthenticated: (auth: boolean) => void;
    
    // UI state
    selectedContactId: number | null;
    setSelectedContact: (id: number | null) => void;
    
    // Filter state
    selectedTags: number[];
    toggleTag: (tagId: number) => void;
    clearTagFilters: () => void;
    
    // Search state
    searchQuery: string;
    setSearchQuery: (query: string) => void;
}

const useAppStore = create<AppState>((set) => ({
    isAuthenticated: false,
    setAuthenticated: (auth) => set({ isAuthenticated: auth }),
    
    selectedContactId: null,
    setSelectedContact: (id) => set({ selectedContactId: id }),
    
    selectedTags: [],
    toggleTag: (tagId) => set((state) => ({
        selectedTags: state.selectedTags.includes(tagId)
            ? state.selectedTags.filter(id => id !== tagId)
            : [...state.selectedTags, tagId]
    })),
    clearTagFilters: () => set({ selectedTags: [] }),
    
    searchQuery: '',
    setSearchQuery: (query) => set({ searchQuery: query }),
}));
```

### 5. Frontend API Client

**Axios Configuration**:
```typescript
import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// API methods
export const apiClient = {
    // Contacts
    getContacts: (params?: ContactFilters) =>
        api.get<Contact[]>('/api/contacts', { params }).then(r => r.data),
    
    getContactProfile: (contactId: number) =>
        api.get<ContactProfile>(`/api/contacts/${contactId}/profile`).then(r => r.data),
    
    syncContacts: () =>
        api.post<SyncJobResponse>('/api/sync/contacts').then(r => r.data),
    
    // Tags
    getTags: () =>
        api.get<Tag[]>('/api/tags').then(r => r.data),
    
    createTag: (data: TagCreate) =>
        api.post<Tag>('/api/tags', data).then(r => r.data),
    
    addTagToContact: (contactId: number, tagId: number) =>
        api.post(`/api/contacts/${contactId}/tags`, { tag_id: tagId }).then(r => r.data),
    
    removeTagFromContact: (contactId: number, tagId: number) =>
        api.delete(`/api/contacts/${contactId}/tags/${tagId}`).then(r => r.data),
    
    // Messages
    sendMessage: (data: SendMessageRequest) =>
        api.post<MessageResult>('/api/messages/send', data).then(r => r.data),
    
    sendBulkMessage: (data: BulkMessageRequest) =>
        api.post<BulkMessageJob>('/api/messages/bulk', data).then(r => r.data),
    
    getBulkMessageStatus: (jobId: string) =>
        api.get<BulkMessageStatus>(`/api/messages/status/${jobId}`).then(r => r.data),
    
    // Auth
    initAuth: (data: AuthInitRequest) =>
        api.post<AuthResponse>('/api/auth/init', data).then(r => r.data),
    
    submitCode: (data: AuthCodeRequest) =>
        api.post<AuthResponse>('/api/auth/code', data).then(r => r.data),
    
    submitPassword: (data: AuthPasswordRequest) =>
        api.post<AuthResponse>('/api/auth/password', data).then(r => r.data),
    
    getAuthStatus: () =>
        api.get<AuthStatusResponse>('/api/auth/status').then(r => r.data),
    
    // Media URLs
    getProfilePhotoUrl: (filename: string) =>
        `${api.defaults.baseURL}/api/media/profile-photos/${filename}`,
    
    getGroupPhotoUrl: (filename: string) =>
        `${api.defaults.baseURL}/api/media/group-photos/${filename}`,
};
```

### 6. UI/UX Design and Page Layouts

**Purpose**: Define the user interface structure and navigation flow

**Application Routes**:
```typescript
const routes = [
    { path: '/', element: <ContactsPage /> },
    { path: '/contacts/:id', element: <ContactDetailPage /> },
    { path: '/tags', element: <TagsPage /> },
    { path: '/messages/bulk', element: <BulkMessagingPage /> },
    { path: '/auth', element: <AuthPage /> },
    { path: '/settings', element: <SettingsPage /> },
];
```

**Main Layout Structure**:
```
┌─────────────────────────────────────────────────────────────┐
│  Header: App Title | Search Bar | Sync Button | User Menu   │
├─────────────┬───────────────────────────────────────────────┤
│  Sidebar    │             Main Content Area                 │
│             │                                                │
│  Navigation │  Current Page Component                       │
│  - Contacts │  (ContactsPage, ContactDetailPage, etc.)      │
│  - Tags     │                                                │
│  - Messages │                                                │
│  - Settings │                                                │
│             │                                                │
│  Tag Filter │                                                │
│  - Tag 1    │                                                │
│  - Tag 2    │                                                │
│  - Tag 3    │                                                │
└─────────────┴───────────────────────────────────────────────┘
```

**ContactsPage Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  Search: [____________] | Filter: [Tags▼] | [Sync Button]   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Contact List (Grid or List View)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ [Photo]  │  │ [Photo]  │  │ [Photo]  │                  │
│  │ Name     │  │ Name     │  │ Name     │                  │
│  │ @user    │  │ @user    │  │ @user    │                  │
│  │ Tag Tag  │  │ Tag      │  │ Tag Tag  │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ [Photo]  │  │ [Photo]  │  │ [Photo]  │                  │
│  │ ...      │  │ ...      │  │ ...      │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│                                                              │
│  [Load More] or Infinite Scroll                             │
└─────────────────────────────────────────────────────────────┘
```

**ContactDetailPage Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  [← Back to Contacts]                                        │
├─────────────────────────────────────────────────────────────┤
│  Profile Section                                             │
│  ┌──────────────┐                                            │
│  │              │   Name: John Doe                           │
│  │  [Profile    │   Username: @johndoe                       │
│  │   Photo]     │   Phone: +1234567890                       │
│  │   Large      │                                            │
│  │              │   Tags: [Work] [Friend] [+]                │
│  └──────────────┘                                            │
├─────────────────────────────────────────────────────────────┤
│  Mutual Groups (3)                                           │
│  ┌────────┐  ┌────────┐  ┌────────┐                         │
│  │[Photo] │  │[Photo] │  │[Photo] │                         │
│  │Group 1 │  │Group 2 │  │Group 3 │                         │
│  │50 mbrs │  │120 mbrs│  │30 mbrs │                         │
│  └────────┘  └────────┘  └────────┘                         │
├─────────────────────────────────────────────────────────────┤
│  Last Messages                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ From John: "Hey, how are you?"                      │    │
│  │ 2 hours ago                                         │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ To John: "I'm good, thanks!"                        │    │
│  │ 1 hour ago                                          │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│  Actions                                                     │
│  [Send Message] [View in Telegram]                          │
└─────────────────────────────────────────────────────────────┘
```

**TagsPage Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  All Tags | [+ Create New Tag]                              │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────┐     │
│  │ [Work] 🔵 (15 contacts)         [Edit] [Delete]    │     │
│  │ [Friends] 🟢 (32 contacts)      [Edit] [Delete]    │     │
│  │ [Family] 🔴 (8 contacts)        [Edit] [Delete]    │     │
│  │ [Clients] 🟡 (23 contacts)      [Edit] [Delete]    │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  Quick Actions                                               │
│  - Send message to contacts with tag                        │
│  - View all contacts with tag                               │
└─────────────────────────────────────────────────────────────┘
```

**BulkMessagingPage Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  Send Bulk Message                                           │
├─────────────────────────────────────────────────────────────┤
│  Step 1: Select Tags                                         │
│  ☑ Work (15 contacts)                                        │
│  ☐ Friends (32 contacts)                                     │
│  ☑ Clients (23 contacts)                                     │
│                                                              │
│  Total Recipients: 38 contacts                               │
├─────────────────────────────────────────────────────────────┤
│  Step 2: Compose Message                                     │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Type your message here...                          │     │
│  │                                                     │     │
│  │                                                     │     │
│  └────────────────────────────────────────────────────┘     │
│  Characters: 0/4096                                          │
├─────────────────────────────────────────────────────────────┤
│  Step 3: Preview Recipients                                  │
│  [John Doe] [Jane Smith] [Bob Wilson] ... [Show All]        │
├─────────────────────────────────────────────────────────────┤
│  [Cancel]                              [Send to 38 contacts] │
└─────────────────────────────────────────────────────────────┘
```

**AuthPage Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│                    Telegram Contact Manager                  │
│                                                              │
│                    Authentication Required                   │
│  ┌────────────────────────────────────────────────────┐     │
│  │                                                     │     │
│  │  API ID:     [________________]                    │     │
│  │                                                     │     │
│  │  API Hash:   [________________]                    │     │
│  │                                                     │     │
│  │  Phone:      [________________]                    │     │
│  │                                                     │     │
│  │  [Get API credentials from my.telegram.org]        │     │
│  │                                                     │     │
│  │                         [Connect]                   │     │
│  │                                                     │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  OR (if code sent)                                           │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Verification Code: [______]                       │     │
│  │                                        [Verify]     │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

**Navigation Flow**:
```
Auth Required → Auth Page → Enter Credentials → Verify Code
                                  ↓
                            Initial Sync (Progress Dialog)
                                  ↓
                            Contacts Page (Main View)
                                  ↓
                    ┌─────────────┼─────────────┐
                    ↓             ↓             ↓
            Contact Detail    Tags Page    Bulk Messaging
                    ↓             ↓             ↓
            Send Message    Manage Tags    Send to Multiple
```

**Responsive Design Breakpoints**:
- Mobile (< 768px): Single column, collapsible sidebar, stacked layout
- Tablet (768px - 1024px): Two column, persistent sidebar
- Desktop (> 1024px): Multi-column, full sidebar with filters

**Color Scheme and Theming**:
- Primary: Blue (#1976d2) - for actions and links
- Secondary: Green (#4caf50) - for success states
- Warning: Orange (#ff9800) - for warnings
- Error: Red (#f44336) - for errors
- Background: White (#ffffff) / Dark (#121212) for dark mode
- Surface: Light Gray (#f5f5f5) / Dark Gray (#1e1e1e) for cards
- Text: Dark Gray (#333333) / Light Gray (#e0e0e0)

**Loading States**:
- Skeleton screens for contact cards
- Spinner for long operations (sync, bulk send)
- Progress bars for trackable operations
- Toast notifications for completed actions

**Error States**:
- Inline error messages for form validation
- Alert dialogs for critical errors
- Retry buttons for failed operations
- Fallback UI for missing images

### 7. Telegram Client Wrapper

**Purpose**: Abstraction layer over Telethon client for domain-specific operations

**Key Methods**:
```python
class TelegramClientWrapper:
    async def connect(self, api_id: int, api_hash: str, phone: str) -> bool
    async def send_code_request(self, phone: str) -> str
    async def sign_in(self, phone: str, code: str, password: str = None) -> bool
    async def get_all_dialogs() -> List[Dialog]
    async def get_dialog_messages(dialog_id: int, limit: int = 100) -> List[Message]
    async def get_user_info(user_id: int) -> User
    async def get_chat_info(chat_id: int) -> Chat
    async def download_profile_photo(entity, file_path: str) -> bool
    async def send_message(user_id: int, message: str) -> bool
    async def get_common_groups(user_id: int) -> List[Chat]
    def is_authenticated() -> bool
    async def disconnect()
```

**Error Handling**: Wraps Telethon exceptions into domain-specific exceptions

### 2. Contact Service

**Purpose**: Core business logic for contact management

**Key Methods**:
```python
class ContactService:
    async def discover_contacts() -> int
    async def get_contact_by_id(contact_id: int) -> Contact
    async def get_all_contacts(filter: ContactFilter = None) -> List[Contact]
    async def search_contacts(query: str) -> List[Contact]
    async def get_contact_profile(contact_id: int) -> ContactProfile
    async def refresh_contact(contact_id: int) -> Contact
    async def sync_all_contacts() -> SyncResult
```

**ContactProfile Structure**:
- Contact basic info
- Profile image path
- List of mutual groups with details
- Last received message
- Last sent message
- Assigned tags

### 3. Tag Service

**Purpose**: Manage contact tagging and categorization

**Key Methods**:
```python
class TagService:
    async def create_tag(name: str, color: str = None) -> Tag
    async def get_all_tags() -> List[Tag]
    async def get_tag_by_id(tag_id: int) -> Tag
    async def add_tag_to_contact(contact_id: int, tag_id: int) -> bool
    async def remove_tag_from_contact(contact_id: int, tag_id: int) -> bool
    async def get_contacts_by_tag(tag_id: int) -> List[Contact]
    async def get_contacts_by_tags(tag_ids: List[int]) -> List[Contact]
    async def delete_tag(tag_id: int) -> bool
    async def update_tag(tag_id: int, name: str = None, color: str = None) -> Tag
```

### 4. Messaging Service

**Purpose**: Handle message sending operations, including bulk messaging

**Key Methods**:
```python
class MessagingService:
    async def send_to_contact(contact_id: int, message: str) -> MessageResult
    async def send_to_tag(tag_id: int, message: str) -> BulkMessageResult
    async def send_to_multiple_tags(tag_ids: List[int], message: str) -> BulkMessageResult
    async def get_last_received_message(contact_id: int) -> Message
    async def get_last_sent_message(contact_id: int) -> Message
```

**BulkMessageResult Structure**:
- Total contacts
- Successful sends
- Failed sends
- List of failures with reasons
- Duration

### 5. Sync Service

**Purpose**: Keep local data synchronized with Telegram

**Key Methods**:
```python
class SyncService:
    async def initial_sync() -> SyncResult
    async def sync_contacts() -> SyncResult
    async def sync_contact_details(contact_id: int) -> bool
    async def sync_messages() -> SyncResult
    async def sync_groups() -> SyncResult
    async def schedule_periodic_sync(interval_minutes: int)
```

### 6. Authentication Service

**Purpose**: Manage Telegram authentication flow

**Key Methods**:
```python
class AuthService:
    async def initiate_auth(api_id: int, api_hash: str) -> bool
    async def request_code(phone: str) -> str
    async def verify_code(phone: str, code: str) -> AuthResult
    async def verify_password(password: str) -> AuthResult
    async def check_session() -> bool
    async def logout() -> bool
    def get_session_info() -> SessionInfo
```

### 7. Repository Interfaces

**Contact Repository**:
```python
class ContactRepository:
    def create(contact: Contact) -> Contact
    def get_by_id(contact_id: int) -> Contact
    def get_by_telegram_id(telegram_id: int) -> Contact
    def get_all(limit: int = None, offset: int = 0) -> List[Contact]
    def update(contact: Contact) -> Contact
    def delete(contact_id: int) -> bool
    def search(query: str) -> List[Contact]
    def exists(telegram_id: int) -> bool
```

**Tag Repository**:
```python
class TagRepository:
    def create(tag: Tag) -> Tag
    def get_by_id(tag_id: int) -> Tag
    def get_by_name(name: str) -> Tag
    def get_all() -> List[Tag]
    def update(tag: Tag) -> Tag
    def delete(tag_id: int) -> bool
    def get_tags_for_contact(contact_id: int) -> List[Tag]
    def add_tag_to_contact(contact_id: int, tag_id: int) -> bool
    def remove_tag_from_contact(contact_id: int, tag_id: int) -> bool
```

**Message Repository**:
```python
class MessageRepository:
    def create(message: Message) -> Message
    def get_last_received(contact_id: int) -> Message
    def get_last_sent(contact_id: int) -> Message
    def get_conversation(contact_id: int, limit: int = 50) -> List[Message]
    def update_last_messages(contact_id: int, received: Message, sent: Message) -> bool
```

**Group Repository**:
```python
class GroupRepository:
    def create(group: Group) -> Group
    def get_by_id(group_id: int) -> Group
    def get_by_telegram_id(telegram_id: int) -> Group
    def get_all() -> List[Group]
    def update(group: Group) -> Group
    def get_mutual_groups(contact_id: int) -> List[Group]
    def add_member(group_id: int, contact_id: int) -> bool
    def remove_member(group_id: int, contact_id: int) -> bool
```

## Data Models

### Database Schema

```sql
-- Contacts table
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    display_name TEXT,
    phone TEXT,
    profile_photo_path TEXT,
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Groups table
CREATE TABLE groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    member_count INTEGER DEFAULT 0,
    profile_photo_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tags table
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    color TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contact-Tag association (many-to-many)
CREATE TABLE contact_tags (
    contact_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (contact_id, tag_id),
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Contact-Group association (many-to-many)
CREATE TABLE contact_groups (
    contact_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (contact_id, group_id),
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
);

-- Messages table
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_message_id INTEGER,
    contact_id INTEGER NOT NULL,
    is_outgoing BOOLEAN NOT NULL,
    content TEXT,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
);

-- Session configuration
CREATE TABLE session_config (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sync status tracking
CREATE TABLE sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sync_type TEXT NOT NULL,
    status TEXT NOT NULL,
    records_processed INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_contacts_telegram_id ON contacts(telegram_id);
CREATE INDEX idx_contacts_username ON contacts(username);
CREATE INDEX idx_groups_telegram_id ON groups(telegram_id);
CREATE INDEX idx_messages_contact_id ON messages(contact_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp);
CREATE INDEX idx_contact_tags_tag_id ON contact_tags(tag_id);
CREATE INDEX idx_contact_groups_group_id ON contact_groups(group_id);
```

### Domain Models

**Contact**:
```python
@dataclass
class Contact:
    id: Optional[int]
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    display_name: str
    phone: Optional[str]
    profile_photo_path: Optional[str]
    bio: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    @property
    def full_name(self) -> str:
        parts = [self.first_name, self.last_name]
        return ' '.join(filter(None, parts)) or self.username or f"User {self.telegram_id}"
```

**Group**:
```python
@dataclass
class Group:
    id: Optional[int]
    telegram_id: int
    name: str
    member_count: int
    profile_photo_path: Optional[str]
    created_at: datetime
    updated_at: datetime
```

**Tag**:
```python
@dataclass
class Tag:
    id: Optional[int]
    name: str
    color: Optional[str]
    created_at: datetime
```

**Message**:
```python
@dataclass
class Message:
    id: Optional[int]
    telegram_message_id: Optional[int]
    contact_id: int
    is_outgoing: bool
    content: Optional[str]
    timestamp: datetime
    created_at: datetime
```

**ContactProfile** (Aggregated View):
```python
@dataclass
class ContactProfile:
    contact: Contact
    tags: List[Tag]
    mutual_groups: List[Group]
    last_received_message: Optional[Message]
    last_sent_message: Optional[Message]
```

### Configuration Model

```python
@dataclass
class AppConfig:
    api_id: int
    api_hash: str
    phone: str
    session_name: str
    database_path: str
    media_storage_path: str
    rate_limit_delay: float = 1.0
    max_retries: int = 3
    sync_interval_minutes: int = 60
```

## Error Handling

### Exception Hierarchy

```python
class TelegramManagerException(Exception):
    """Base exception for all application errors"""
    pass

class AuthenticationError(TelegramManagerException):
    """Raised when authentication fails"""
    pass

class APIError(TelegramManagerException):
    """Raised when Telegram API returns an error"""
    pass

class RateLimitError(APIError):
    """Raised when rate limit is exceeded"""
    pass

class NetworkError(TelegramManagerException):
    """Raised when network connectivity issues occur"""
    pass

class DatabaseError(TelegramManagerException):
    """Raised when database operations fail"""
    pass

class ValidationError(TelegramManagerException):
    """Raised when input validation fails"""
    pass

class ContactNotFoundError(TelegramManagerException):
    """Raised when a contact cannot be found"""
    pass
```

### Error Handling Strategy

1. **API Errors**: Wrap Telethon exceptions and add context
   - Retry on transient errors (network issues, timeouts)
   - Surface authentication errors to user immediately
   - Log all API errors with full context

2. **Rate Limiting**: 
   - Detect rate limit errors from Telegram API
   - Implement exponential backoff
   - Show progress to user during delays
   - Store failed operations for retry

3. **Database Errors**:
   - Use transactions for multi-step operations
   - Rollback on failure
   - Log database errors for debugging
   - Show user-friendly error messages

4. **Validation Errors**:
   - Validate input at service layer
   - Provide specific error messages
   - Prevent invalid data from reaching repositories

5. **Graceful Degradation**:
   - Continue operations when individual items fail (e.g., bulk messaging)
   - Collect and report all failures at the end
   - Allow users to retry failed operations

### Retry Logic

```python
class RetryStrategy:
    max_attempts: int = 3
    initial_delay: float = 1.0
    backoff_factor: float = 2.0
    
    async def execute_with_retry(self, operation: Callable, *args, **kwargs):
        """Execute operation with exponential backoff retry"""
        for attempt in range(self.max_attempts):
            try:
                return await operation(*args, **kwargs)
            except (NetworkError, RateLimitError) as e:
                if attempt == self.max_attempts - 1:
                    raise
                delay = self.initial_delay * (self.backoff_factor ** attempt)
                await asyncio.sleep(delay)
```

## Testing Strategy

### Unit Testing

**Scope**: Individual components in isolation

**Approach**:
- Mock external dependencies (Telegram client, database)
- Test each service method independently
- Validate business logic and edge cases
- Use pytest with pytest-asyncio for async tests
- Aim for >80% code coverage

**Key Test Areas**:
- Contact discovery and consolidation logic
- Tag assignment and filtering
- Message sending logic
- Data validation
- Error handling

**Example Test Structure**:
```python
class TestContactService:
    @pytest.fixture
    def mock_client(self):
        return Mock(spec=TelegramClientWrapper)
    
    @pytest.fixture
    def mock_repository(self):
        return Mock(spec=ContactRepository)
    
    @pytest.fixture
    def service(self, mock_client, mock_repository):
        return ContactService(mock_client, mock_repository)
    
    @pytest.mark.asyncio
    async def test_discover_contacts_consolidates_duplicates(self, service):
        # Test that duplicate contacts are merged
        pass
```

### Integration Testing

**Scope**: Interaction between components

**Approach**:
- Use real SQLite database (in-memory for speed)
- Mock only the Telegram API client
- Test full workflows end-to-end
- Verify data persistence and retrieval

**Key Test Areas**:
- Authentication flow
- Contact discovery and storage
- Tag management with database
- Bulk messaging workflow
- Sync operations

### Manual Testing Checklist

**Authentication**:
- [ ] First-time authentication with phone number
- [ ] Code verification
- [ ] 2FA password entry
- [ ] Session persistence across restarts
- [ ] Re-authentication on session expiry

**Contact Discovery**:
- [ ] Initial scan of all chats
- [ ] Duplicate contact consolidation
- [ ] Profile photo download
- [ ] Mutual group detection

**Contact Management**:
- [ ] View contact list
- [ ] Search by name/username
- [ ] Filter by tags
- [ ] View contact profile
- [ ] Display mutual groups

**Tagging**:
- [ ] Create new tag
- [ ] Add tag to contact
- [ ] Remove tag from contact
- [ ] Filter contacts by tag
- [ ] Delete tag

**Bulk Messaging**:
- [ ] Select contacts by tag
- [ ] Preview recipient list
- [ ] Send messages with progress feedback
- [ ] Handle send failures
- [ ] View send summary

**Error Scenarios**:
- [ ] No internet connection
- [ ] Invalid API credentials
- [ ] Rate limit exceeded
- [ ] Session expired
- [ ] Contact not found

### Performance Testing

**Key Metrics**:
- Contact discovery time for 100, 500, 1000+ contacts
- Message sending throughput
- Database query performance with large datasets
- Memory usage during sync operations
- UI responsiveness

**Performance Targets**:
- Contact discovery: <5 seconds per 100 contacts
- Single message send: <2 seconds
- Database queries: <100ms for typical operations
- Bulk message sending: 10-15 messages per minute (respecting rate limits)

## Security Considerations

1. **Credentials Storage**:
   - Store API credentials in environment variables
   - Never commit credentials to version control
   - Use system keyring for session storage (optional enhancement)

2. **Session Management**:
   - Store Telegram session files securely
   - Set appropriate file permissions (600)
   - Clear sessions on logout

3. **Data Privacy**:
   - All data stored locally
   - No external data transmission except to Telegram API
   - Provide option to export/delete all data

4. **Input Validation**:
   - Sanitize all user inputs
   - Validate phone numbers and codes
   - Prevent SQL injection through parameterized queries

## Deployment Considerations

### Installation Requirements

```
Python 3.9+
Dependencies:
- telethon>=1.28
- aiosqlite>=0.19
- python-dotenv>=1.0
- rich>=13.0
- pillow>=10.0
- pytest>=7.0 (dev)
- pytest-asyncio>=0.21 (dev)
```

### Directory Structure

```
telegram-manager/
├── backend/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry
│   │   ├── config.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── contact.py
│   │   │   ├── group.py
│   │   │   ├── tag.py
│   │   │   └── message.py
│   │   ├── schemas/                # Pydantic schemas for API
│   │   │   ├── __init__.py
│   │   │   ├── contact.py
│   │   │   ├── tag.py
│   │   │   ├── message.py
│   │   │   └── auth.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py             # Dependencies
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── contacts.py
│   │   │   │   ├── tags.py
│   │   │   │   ├── messages.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── media.py
│   │   │   │   └── sync.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── contact_repository.py
│   │   │   ├── tag_repository.py
│   │   │   ├── message_repository.py
│   │   │   └── group_repository.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── contact_service.py
│   │   │   ├── tag_service.py
│   │   │   ├── messaging_service.py
│   │   │   ├── sync_service.py
│   │   │   └── auth_service.py
│   │   ├── telegram/
│   │   │   ├── __init__.py
│   │   │   └── client_wrapper.py
│   │   └── database/
│   │       ├── __init__.py
│   │       ├── connection.py
│   │       └── migrations.py
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   ├── data/
│   │   ├── contacts.db
│   │   ├── sessions/
│   │   └── media/
│   │       ├── profile-photos/
│   │       └── group-photos/
│   ├── .env.example
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── main.tsx               # React app entry
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── ContactList.tsx
│   │   │   ├── ContactProfile.tsx
│   │   │   ├── ContactCard.tsx
│   │   │   ├── TagManager.tsx
│   │   │   ├── TagChip.tsx
│   │   │   ├── MessageComposer.tsx
│   │   │   ├── BulkMessageDialog.tsx
│   │   │   ├── AuthForm.tsx
│   │   │   ├── SearchBar.tsx
│   │   │   ├── ProfileImage.tsx
│   │   │   ├── GroupList.tsx
│   │   │   └── LoadingSpinner.tsx
│   │   ├── pages/
│   │   │   ├── ContactsPage.tsx
│   │   │   ├── ContactDetailPage.tsx
│   │   │   ├── TagsPage.tsx
│   │   │   ├── MessagingPage.tsx
│   │   │   └── AuthPage.tsx
│   │   ├── hooks/
│   │   │   ├── useContacts.ts
│   │   │   ├── useTags.ts
│   │   │   ├── useAuth.ts
│   │   │   └── useMessages.ts
│   │   ├── services/
│   │   │   └── api.ts             # API client
│   │   ├── store/
│   │   │   └── authStore.ts       # Client state
│   │   ├── types/
│   │   │   ├── contact.ts
│   │   │   ├── tag.ts
│   │   │   ├── message.ts
│   │   │   └── auth.ts
│   │   └── utils/
│   │       ├── formatters.ts
│   │       └── validators.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── README.md
├── docker-compose.yml             # Optional: for containerization
└── README.md
```
</text>

<old_text line=732>
### Installation Requirements

```
Python 3.9+
Dependencies:
- telethon>=1.28
- aiosqlite>=0.19
- python-dotenv>=1.0
- rich>=13.0
- pillow>=10.0
- pytest>=7.0 (dev)
- pytest-asyncio>=0.21 (dev)
```

### Development Setup

**Backend Setup**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
uvicorn src.main:app --reload --port 8000
```

**Frontend Setup**:
```bash
cd frontend
npm install  # or yarn install
cp .env.example .env
# Edit .env with API URL (VITE_API_URL=http://localhost:8000)
npm run dev  # or yarn dev
```

### First-Run User Experience

1. Backend server starts on http://localhost:8000 (API docs at /docs)
2. Frontend development server starts on http://localhost:5173
3. User opens web browser and navigates to http://localhost:5173
4. User is presented with authentication page
5. User provides API credentials through web form (obtained from my.telegram.org)
6. Backend creates database and necessary directories
7. User completes phone verification and optional 2FA
8. Initial contact discovery runs (with progress bar displayed in UI)
9. User presented with main dashboard showing contacts with profile photos
10. User can browse contacts, view profiles with images, add tags, and send messages

### Production Deployment

**Option 1: Single Server Deployment**
- Build frontend: `npm run build` (creates static files in `dist/`)
- Serve frontend static files via FastAPI's StaticFiles
- Run FastAPI with production server: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app`
- Use nginx as reverse proxy for SSL and caching

**Option 2: Separate Hosting**
- Deploy backend to service like Railway, Render, or DigitalOcean
- Deploy frontend to Vercel, Netlify, or Cloudflare Pages
- Configure CORS appropriately
- Set environment variables for API URLs

**Docker Deployment** (using docker-compose.yml):
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_PATH=/app/data/contacts.db
      - MEDIA_PATH=/app/data/media
  
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    environment:
      - VITE_API_URL=http://localhost:8000
```

## Future Enhancements

1. **Real-time Updates**: WebSocket integration for live sync and notifications
2. **Advanced Filtering**: Complex queries combining multiple criteria with UI
3. **Contact Notes**: Add personal notes to contacts
4. **Message Templates**: Save and reuse message templates
5. **Scheduled Messages**: Schedule bulk messages for future sending
6. **Analytics Dashboard**: Track messaging patterns and engagement with charts
7. **Export/Import**: Export contacts and tags to CSV/JSON
8. **Multi-Account Support**: Manage multiple Telegram accounts
9. **Dark Mode**: Theme switching support
10. **Contact Groups**: Create custom contact groups beyond tags
11. **Image Carousel**: Swipe through contact and group photos
12. **Notification System**: Toast notifications for background operations
13. **Accessibility**: Full ARIA support and keyboard navigation
14. **Internationalization**: Multi-language support
11. **Mobile Responsive**: Optimize UI for mobile devices
12. **Progressive Web App**: Add PWA support for offline capabilities
13. **Image Gallery**: View all shared media with contacts
14. **Advanced Search**: Fuzzy search with filters
15. **Bulk Operations**: Select multiple contacts for batch operations