# Implementation Plan

## Backend Implementation

- [ ] 1. Set up project structure and dependencies
  - Create backend directory structure with src/, tests/, data/ folders
  - Create requirements.txt with FastAPI, Telethon, SQLite, Pydantic, python-dotenv, Pillow, pytest dependencies
  - Create .env.example with API_ID, API_HASH, DATABASE_PATH, MEDIA_PATH, SESSION_NAME configuration variables
  - Create main.py with basic FastAPI application initialization
  - _Requirements: 6.1, 6.2_

- [ ] 2. Implement database schema and connection management
  - Create database/connection.py with SQLite connection utilities and async context manager
  - Create database/migrations.py with SQL schema for contacts, groups, tags, contact_tags, contact_groups, messages, session_config, and sync_log tables
  - Implement migration function to create all tables with proper indexes
  - Write unit tests for database connection and schema creation
  - _Requirements: 1.4, 2.1, 3.3, 7.1_

- [x] 3. Create domain models and data classes
  - Create models/contact.py with Contact dataclass including id, telegram_id, username, first_name, last_name, display_name, phone, profile_photo_path, bio, timestamps
  - Create models/group.py with Group dataclass including id, telegram_id, name, member_count, profile_photo_path, timestamps
  - Create models/tag.py with Tag dataclass including id, name, color, created_at
  - Create models/message.py with Message dataclass including id, telegram_message_id, contact_id, is_outgoing, content, timestamp
  - Add property methods for computed fields (e.g., full_name on Contact)
  - _Requirements: 1.4, 2.1, 2.4, 2.5, 3.4_

- [x] 4. Implement Pydantic schemas for API requests and responses
  - Create schemas/contact.py with ContactResponse, ContactProfileResponse, GroupInfo, MessageInfo schemas
  - Create schemas/tag.py with TagCreate, TagUpdate, TagResponse schemas
  - Create schemas/message.py with SendMessageRequest, BulkMessageRequest, MessageResult, BulkMessageJob, BulkMessageStatus schemas
  - Create schemas/auth.py with AuthInitRequest, AuthCodeRequest, AuthPasswordRequest, AuthResponse, AuthStatusResponse schemas
  - Add validation rules and example values for API documentation
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 5. Build Contact Repository with CRUD operations
  - Create repositories/contact_repository.py with ContactRepository class
  - Implement create, get_by_id, get_by_telegram_id, get_all, update, delete, search, exists methods
  - Use parameterized queries to prevent SQL injection
  - Write unit tests for all repository methods using in-memory SQLite database
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 4.1, 4.3_

- [x] 6. Build Tag Repository with many-to-many relationship management
  - Create repositories/tag_repository.py with TagRepository class
  - Implement create, get_by_id, get_by_name, get_all, update, delete methods for tags
  - Implement get_tags_for_contact, add_tag_to_contact, remove_tag_from_contact methods for associations
  - Implement get_contacts_by_tag for filtering
  - Write unit tests for tag operations and contact-tag associations
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.4_

- [ ] 7. Build Group and Message Repositories
  - Create repositories/group_repository.py with GroupRepository class implementing create, get_by_id, get_by_telegram_id, get_all, update, get_mutual_groups, add_member, remove_member methods
  - Create repositories/message_repository.py with MessageRepository class implementing create, get_last_received, get_last_sent, get_conversation, update_last_messages methods
  - Write unit tests for group membership tracking and message retrieval
  - _Requirements: 2.2, 2.3, 2.4, 2.5, 7.4_

- [ ] 8. Implement Telegram Client Wrapper for authentication
  - Create telegram/client_wrapper.py with TelegramClientWrapper class
  - Implement connect, send_code_request, sign_in methods using Telethon client
  - Implement is_authenticated, disconnect methods
  - Add error handling for authentication failures and wrap Telethon exceptions
  - Write unit tests with mocked Telethon client
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 8.2_

- [ ] 9. Extend Telegram Client Wrapper for data fetching
  - Implement get_all_dialogs method to fetch all chats, groups, and supergroups
  - Implement get_dialog_messages method to retrieve message history with limit parameter
  - Implement get_user_info and get_chat_info methods to fetch entity details
  - Implement get_common_groups method to find mutual groups with a user
  - Add retry logic with exponential backoff for transient network errors
  - Write unit tests for data fetching methods
  - _Requirements: 1.1, 2.2, 2.3, 2.4, 2.5, 8.1, 8.4_

- [ ] 10. Add media handling to Telegram Client Wrapper
  - Implement download_profile_photo method to download and save profile images
  - Create utility function to generate unique filenames for media files
  - Implement image resizing using Pillow for thumbnails and full-size versions
  - Add error handling for missing or inaccessible profile photos
  - Write unit tests for media download and processing
  - _Requirements: 1.4, 2.1, 2.6, 2.3_

- [ ] 11. Implement Authentication Service
  - Create services/auth_service.py with AuthService class
  - Implement initiate_auth, request_code, verify_code, verify_password methods
  - Implement check_session, logout, get_session_info methods
  - Store session configuration in database using session_config table
  - Add validation for phone numbers and verification codes
  - Write unit tests for authentication flow with mocked dependencies
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 8.2_

- [ ] 12. Implement Contact Service for discovery and management
  - Create services/contact_service.py with ContactService class
  - Implement discover_contacts method to scan all dialogs and extract unique contacts
  - Implement consolidation logic to merge duplicate contacts by telegram_id
  - Implement get_contact_by_id, get_all_contacts, search_contacts methods
  - Implement get_contact_profile method to aggregate contact data, tags, groups, and messages
  - Implement refresh_contact and sync_all_contacts methods
  - Write unit tests for contact discovery, consolidation, and profile aggregation
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 2.5, 4.1, 4.2, 4.3_

- [ ] 13. Implement Tag Service for contact organization
  - Create services/tag_service.py with TagService class
  - Implement create_tag, get_all_tags, get_tag_by_id, update_tag, delete_tag methods
  - Implement add_tag_to_contact and remove_tag_from_contact methods with validation
  - Implement get_contacts_by_tag and get_contacts_by_tags methods for filtering
  - Add color validation for tag colors
  - Write unit tests for tag management and contact-tag associations
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.4_

- [ ] 14. Implement Messaging Service for sending messages
  - Create services/messaging_service.py with MessagingService class
  - Implement send_to_contact method to send message to single contact
  - Implement get_last_received_message and get_last_sent_message methods
  - Add error handling for failed message sends with detailed error messages
  - Implement rate limiting awareness to respect Telegram API limits
  - Write unit tests for single message sending
  - _Requirements: 5.4, 2.4, 2.5, 8.1, 8.3, 8.4_

- [ ] 15. Implement bulk messaging functionality in Messaging Service
  - Implement send_to_tag method to send messages to all contacts with a tag
  - Implement send_to_multiple_tags method to send to contacts matching any selected tag
  - Create background job system for tracking bulk send progress
  - Implement progress tracking with sent count, failed count, and error collection
  - Add automatic retry logic for failed sends with rate limit handling
  - Write unit tests for bulk messaging with multiple success and failure scenarios
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 8.4_

- [ ] 16. Implement Sync Service for data synchronization
  - Create services/sync_service.py with SyncService class
  - Implement initial_sync method to perform first-time contact and group discovery
  - Implement sync_contacts method to update contact information from Telegram
  - Implement sync_contact_details to refresh single contact data including profile photo
  - Implement sync_messages method to update last message information
  - Implement sync_groups method to update group memberships
  - Add sync logging to sync_log table for tracking sync operations
  - Write unit tests for sync operations
  - _Requirements: 1.3, 7.1, 7.2, 7.3, 7.4_

- [ ] 17. Create Contact API endpoints
  - Create api/routes/contacts.py with contact router
  - Implement GET /api/contacts endpoint with pagination, search, and tag filtering
  - Implement GET /api/contacts/{contact_id} endpoint for contact details
  - Implement GET /api/contacts/{contact_id}/profile endpoint for full profile with aggregated data
  - Add request validation and error handling with appropriate HTTP status codes
  - Write integration tests for contact endpoints
  - _Requirements: 1.1, 1.4, 2.1, 2.2, 2.3, 2.4, 2.5, 4.1, 4.2, 4.3_

- [ ] 18. Create Tag API endpoints
  - Create api/routes/tags.py with tag router
  - Implement GET /api/tags endpoint to list all tags with contact counts
  - Implement POST /api/tags endpoint to create new tags
  - Implement PUT /api/tags/{tag_id} endpoint to update tag name or color
  - Implement DELETE /api/tags/{tag_id} endpoint to delete tags
  - Implement POST /api/contacts/{contact_id}/tags and DELETE /api/contacts/{contact_id}/tags/{tag_id} endpoints for tag assignment
  - Write integration tests for tag management
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [ ] 19. Create Messaging API endpoints
  - Create api/routes/messages.py with messaging router
  - Implement POST /api/messages/send endpoint for single message sending
  - Implement POST /api/messages/bulk endpoint to initiate bulk message job
  - Implement GET /api/messages/status/{job_id} endpoint to check bulk message progress
  - Add WebSocket endpoint (optional) for real-time bulk send progress updates
  - Write integration tests for messaging endpoints
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [ ] 20. Create Authentication API endpoints
  - Create api/routes/auth.py with authentication router
  - Implement POST /api/auth/init endpoint to initiate authentication with API credentials
  - Implement POST /api/auth/code endpoint to submit verification code
  - Implement POST /api/auth/password endpoint for 2FA password
  - Implement GET /api/auth/status endpoint to check authentication state
  - Implement POST /api/auth/logout endpoint to clear session
  - Write integration tests for authentication flow
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_

- [ ] 21. Create Media and Sync API endpoints
  - Create api/routes/media.py with media router for serving profile and group photos
  - Implement GET /api/media/profile-photos/{filename} endpoint with FileResponse
  - Implement GET /api/media/group-photos/{filename} endpoint
  - Create api/routes/sync.py with sync router
  - Implement POST /api/sync/contacts and POST /api/sync/messages endpoints
  - Implement GET /api/sync/status endpoint to check sync progress
  - Write integration tests for media serving and sync endpoints
  - _Requirements: 1.4, 2.1, 2.3, 7.1, 7.2, 7.3_

- [ ] 22. Wire up FastAPI application with all routes and middleware
  - Update main.py to include all routers with appropriate prefixes
  - Configure CORS middleware to allow frontend origin
  - Add static file mounting for media directory
  - Configure exception handlers for custom exceptions
  - Add startup event handler to initialize database and check authentication
  - Add OpenAPI documentation configuration
  - Write integration tests for complete API
  - _Requirements: All backend requirements_

## Frontend Implementation

- [ ] 23. Set up React project with Vite and dependencies
  - Initialize Vite project with React and TypeScript template
  - Install dependencies: React Router, Material-UI or Tailwind CSS, Axios, React Query, Zustand
  - Create frontend directory structure with src/components, src/pages, src/hooks, src/services, src/types folders
  - Configure Vite for development and production builds
  - Create .env.example with VITE_API_URL configuration
  - _Requirements: 6.1, 6.2_

- [ ] 24. Create TypeScript type definitions
  - Create types/contact.ts with Contact, ContactProfile, GroupInfo types
  - Create types/tag.ts with Tag, TagCreate, TagUpdate types
  - Create types/message.ts with Message, SendMessageRequest, BulkMessageRequest, BulkMessageJob types
  - Create types/auth.ts with AuthInitRequest, AuthResponse, AuthStatusResponse types
  - Ensure types match backend Pydantic schemas
  - _Requirements: All requirements (type safety)_

- [ ] 25. Implement API client service with Axios
  - Create services/api.ts with configured Axios instance
  - Implement contact methods: getContacts, getContactProfile, syncContacts
  - Implement tag methods: getTags, createTag, updateTag, deleteTag, addTagToContact, removeTagFromContact
  - Implement message methods: sendMessage, sendBulkMessage, getBulkMessageStatus
  - Implement auth methods: initAuth, submitCode, submitPassword, getAuthStatus
  - Implement media URL helper methods: getProfilePhotoUrl, getGroupPhotoUrl
  - Add error handling and request/response interceptors
  - _Requirements: All API interaction requirements_

- [ ] 26. Create authentication store and hooks
  - Create store/authStore.ts with Zustand store for authentication state
  - Implement state for isAuthenticated, setAuthenticated, requiresCode, requiresPassword
  - Create hooks/useAuth.ts with custom hooks for authentication operations
  - Implement useAuthStatus hook to check authentication on mount
  - Implement useInitAuth, useSubmitCode, useSubmitPassword mutation hooks
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_

- [ ] 27. Create React Query hooks for contacts
  - Create hooks/useContacts.ts with useContacts hook for fetching contact list
  - Implement useContactProfile hook for fetching full contact profile
  - Implement useSearchContacts hook with debounced search
  - Implement useSyncContacts mutation hook
  - Configure query caching and refetch strategies
  - _Requirements: 1.1, 1.3, 2.1, 2.2, 2.3, 2.4, 2.5, 4.1, 4.3, 7.2_

- [ ] 28. Create React Query hooks for tags and messages
  - Create hooks/useTags.ts with useTags, useCreateTag, useUpdateTag, useDeleteTag hooks
  - Implement useAddTagToContact and useRemoveTagFromContact mutation hooks
  - Create hooks/useMessages.ts with useSendMessage and useSendBulkMessage hooks
  - Implement useBulkMessageStatus hook for polling bulk send progress
  - Configure automatic query invalidation after mutations
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [ ] 29. Build ProfileImage component with lazy loading
  - Create components/ProfileImage.tsx with size variants (small, medium, large)
  - Implement lazy loading using Intersection Observer
  - Add fallback to initials or default avatar when image fails to load
  - Implement loading placeholder with skeleton
  - Add circular and square shape variants
  - Style component with CSS modules or styled components
  - _Requirements: 2.1, 2.6_

- [ ] 30. Build ContactCard component for list display
  - Create components/ContactCard.tsx displaying contact name, username, profile photo, and tags
  - Implement click handler to navigate to contact detail
  - Display tag chips with colors
  - Add hover effects and transitions
  - Make component responsive for mobile and desktop
  - _Requirements: 2.1, 3.4, 3.6, 4.1, 4.2_

- [ ] 31. Build TagChip and TagManager components
  - Create components/TagChip.tsx to display individual tag with color and optional remove button
  - Create components/TagManager.tsx for adding and removing tags from contacts
  - Implement tag creation dialog with color picker
  - Implement autocomplete for selecting existing tags
  - Add inline tag editing capabilities
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [ ] 32. Build SearchBar component with filtering
  - Create components/SearchBar.tsx with debounced input
  - Implement clear button and search icon
  - Add dropdown for tag filter selection with multi-select
  - Display active filters as removable chips
  - Add keyboard shortcuts for focus and clear
  - _Requirements: 4.3, 4.4_

- [ ] 33. Build ContactList component with virtual scrolling
  - Create components/ContactList.tsx using ContactCard components
  - Implement virtual scrolling for performance with large lists
  - Add grid and list view toggle
  - Implement infinite scroll or load more button
  - Show loading skeletons while fetching data
  - Display empty state when no contacts found
  - _Requirements: 4.1, 4.2, 4.5_

- [ ] 34. Build GroupList component for mutual groups display
  - Create components/GroupList.tsx to display group cards with photos
  - Show group name, member count, and profile image
  - Implement grid layout for multiple groups
  - Add empty state for no mutual groups
  - Make groups clickable to open in Telegram (optional)
  - _Requirements: 2.2, 2.3, 2.7_

- [ ] 35. Build MessageComposer component
  - Create components/MessageComposer.tsx with multi-line text input
  - Implement character counter with max length validation
  - Add send button with loading state
  - Implement keyboard shortcuts (Ctrl/Cmd + Enter to send)
  - Show success/error notifications after sending
  - _Requirements: 5.4_

- [ ] 36. Build ContactProfile component for detail view
  - Create components/ContactProfile.tsx displaying full contact information
  - Show large profile photo with ProfileImage component
  - Display contact details (name, username, phone) with proper formatting
  - Show assigned tags with TagManager for editing
  - Display GroupList for mutual groups
  - Show last received and sent messages with timestamps
  - Add send message quick action with MessageComposer
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 3.4_

- [ ] 37. Build BulkMessageDialog component
  - Create components/BulkMessageDialog.tsx with multi-step flow
  - Implement tag selection with checkboxes and contact count preview
  - Add message composition area with MessageComposer
  - Show recipient preview list with contact photos
  - Implement send confirmation with progress tracking
  - Display results summary with success/failure counts and retry option
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [ ] 38. Build AuthForm component for authentication
  - Create components/AuthForm.tsx with multi-step authentication form
  - Implement API credentials input (API ID, API Hash, Phone)
  - Add verification code input when code is required
  - Add 2FA password input when password is required
  - Show clear error messages for authentication failures
  - Add link to get API credentials from my.telegram.org
  - Display loading states during authentication
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 8.2_

- [ ] 39. Create ContactsPage with search and filters
  - Create pages/ContactsPage.tsx as main contacts view
  - Integrate SearchBar for filtering contacts
  - Integrate ContactList to display filtered contacts
  - Add sync button to trigger manual contact sync with progress feedback
  - Show loading state during initial data fetch
  - Implement error boundary for error handling
  - _Requirements: 1.3, 4.1, 4.2, 4.3, 4.4, 4.5, 7.2_

- [ ] 40. Create ContactDetailPage for individual contact view
  - Create pages/ContactDetailPage.tsx with back navigation
  - Integrate ContactProfile component
  - Add route parameter handling for contact ID
  - Implement loading state while fetching contact profile
  - Handle contact not found error with redirect
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_

- [ ] 41. Create TagsPage for tag management
  - Create pages/TagsPage.tsx displaying all tags
  - Show tag list with contact counts, edit and delete buttons
  - Implement create new tag dialog
  - Add edit tag dialog for updating name and color
  - Implement delete confirmation dialog
  - Show quick actions: send message to tag, view contacts with tag
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 42. Create BulkMessagingPage for sending to multiple contacts
  - Create pages/BulkMessagingPage.tsx as dedicated bulk messaging interface
  - Integrate BulkMessageDialog component
  - Show history of previous bulk sends (optional)
  - Add navigation from tags page to bulk messaging with pre-selected tag
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [ ] 43. Create AuthPage for authentication flow
  - Create pages/AuthPage.tsx as authentication screen
  - Integrate AuthForm component
  - Handle authentication success by redirecting to contacts page
  - Show authentication status and allow re-authentication if session expired
  - Display helpful instructions for obtaining API credentials
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_

- [ ] 44. Implement routing and navigation
  - Configure React Router with routes for all pages
  - Implement protected route wrapper to check authentication status
  - Add navigation sidebar with links to Contacts, Tags, Messages, Settings
  - Implement breadcrumb navigation for nested routes
  - Handle 404 not found page
  - _Requirements: All navigation requirements_

- [ ] 45. Create main App layout with header and sidebar
  - Create App.tsx with main layout structure
  - Implement header with app title, search bar, sync button, and user menu
  - Create collapsible sidebar with navigation links
  - Implement tag filter section in sidebar showing all tags
  - Add responsive behavior for mobile (hamburger menu)
  - Apply consistent theming and styling
  - _Requirements: All UI requirements_

- [ ] 46. Implement loading states, error handling, and notifications
  - Create LoadingSpinner component for loading states
  - Create skeleton components for contact cards and profile
  - Implement toast notification system for success/error messages
  - Create error boundary component for catching React errors
  - Add retry buttons for failed operations
  - Implement offline detection and messaging
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [ ] 47. Add responsive design and mobile optimization
  - Implement media queries for mobile (<768px), tablet (768-1024px), and desktop (>1024px) breakpoints
  - Make sidebar collapsible on mobile with hamburger menu
  - Adjust contact list to single column on mobile
  - Optimize image sizes for mobile bandwidth
  - Test touch interactions for mobile devices
  - Ensure all interactive elements are touch-friendly (min 44px)
  - _Requirements: All UI requirements_

- [ ] 48. Implement dark mode support (optional enhancement)
  - Create theme context with light and dark theme definitions
  - Implement theme toggle button in header
  - Update all components to use theme colors
  - Store theme preference in local storage
  - Respect system preference for default theme
  - _Requirements: Future enhancement_

## Integration and Testing

- [ ] 49. Write end-to-end integration tests for contact management flow
  - Set up pytest with async support and test database
  - Write test for complete authentication flow
  - Write test for contact discovery and consolidation
  - Write test for viewing contact profile with all aggregated data
  - Write test for tag assignment and filtering
  - Verify profile photos are downloaded and served correctly
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 2.5, 3.3, 3.4, 6.1-6.8_

- [ ] 50. Write end-to-end integration tests for messaging functionality
  - Write test for sending single message to contact
  - Write test for bulk message sending by tag
  - Write test for bulk message progress tracking
  - Write test for handling send failures and retry logic
  - Verify rate limiting is respected
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 8.4_

- [ ] 51. Write end-to-end frontend tests with React Testing Library
  - Set up Vitest and React Testing Library
  - Write test for ContactList rendering and filtering
  - Write test for ContactProfile display with mocked data
  - Write test for tag management interactions
  - Write test for bulk messaging dialog flow
  - Write test for authentication form submission
  - _Requirements: All frontend requirements_

- [ ] 52. Create development documentation and setup guides
  - Write README.md with project overview and architecture
  - Document backend setup steps with virtual environment and dependencies
  - Document frontend setup steps with npm installation
  - Create API documentation guide (link to FastAPI /docs)
  - Document how to obtain Telegram API credentials
  - Add troubleshooting section for common issues
  - _Requirements: 6.1, 6.2_

- [ ] 53. Set up Docker configuration for deployment
  - Create Dockerfile for backend with Python base image
  - Create Dockerfile for frontend with Node build and nginx serve
  - Create docker-compose.yml to orchestrate backend and frontend services
  - Configure volume mounts for persistent data (database, media)
  - Add health checks for both services
  - Document Docker deployment steps
  - _Requirements: All deployment requirements_

- [ ] 54. Perform manual testing and bug fixes
  - Test complete authentication flow with real Telegram account
  - Test contact discovery with various chat types (private, groups, channels)
  - Verify profile photos display correctly for contacts and groups
  - Test tag creation, assignment, and filtering
  - Test bulk messaging with progress tracking and error handling
  - Verify sync operations update data correctly
  - Test responsive design on mobile, tablet, and desktop
  - Fix any bugs discovered during testing
  - _Requirements: All requirements_