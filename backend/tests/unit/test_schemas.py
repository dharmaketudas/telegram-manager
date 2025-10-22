"""
Unit tests for API schemas.

This module contains comprehensive tests for all Pydantic schemas
to ensure validation rules work correctly.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.schemas.contact import (
    ContactResponse,
    ContactProfileResponse,
    GroupInfo,
    MessageInfo,
)
from src.schemas.tag import TagCreate, TagUpdate, TagResponse
from src.schemas.message import (
    SendMessageRequest,
    BulkMessageRequest,
    MessageResult,
    BulkMessageJob,
    BulkMessageStatus,
)
from src.schemas.auth import (
    AuthInitRequest,
    AuthCodeRequest,
    AuthPasswordRequest,
    AuthResponse,
    AuthStatusResponse,
)


class TestGroupInfo:
    """Tests for GroupInfo schema."""

    def test_group_info_creation(self):
        """Test creating a valid GroupInfo."""
        group = GroupInfo(
            id=1,
            telegram_id=1001234567890,
            name="Python Developers",
            member_count=150,
            profile_photo_url="/api/media/group-photos/1001234567890.jpg",
        )

        assert group.id == 1
        assert group.telegram_id == 1001234567890
        assert group.name == "Python Developers"
        assert group.member_count == 150
        assert group.profile_photo_url == "/api/media/group-photos/1001234567890.jpg"

    def test_group_info_without_photo(self):
        """Test creating GroupInfo without profile photo."""
        group = GroupInfo(
            id=1,
            telegram_id=1001234567890,
            name="Python Developers",
            member_count=150,
            profile_photo_url=None,
        )

        assert group.profile_photo_url is None


class TestMessageInfo:
    """Tests for MessageInfo schema."""

    def test_message_info_creation(self):
        """Test creating a valid MessageInfo."""
        now = datetime.now()
        message = MessageInfo(
            id=1, content="Hello, how are you?", timestamp=now, is_outgoing=True
        )

        assert message.id == 1
        assert message.content == "Hello, how are you?"
        assert message.timestamp == now
        assert message.is_outgoing is True

    def test_message_info_without_content(self):
        """Test creating MessageInfo without content (media-only)."""
        now = datetime.now()
        message = MessageInfo(id=1, content=None, timestamp=now, is_outgoing=False)

        assert message.content is None


class TestContactResponse:
    """Tests for ContactResponse schema."""

    def test_contact_response_creation(self):
        """Test creating a valid ContactResponse."""
        now = datetime.now()
        contact = ContactResponse(
            id=1,
            telegram_id=123456789,
            username="john_doe",
            first_name="John",
            last_name="Doe",
            display_name="John Doe",
            phone="+1234567890",
            profile_photo_url="/api/media/profile-photos/123456789.jpg",
            tags=["Work", "Friend"],
            updated_at=now,
        )

        assert contact.id == 1
        assert contact.telegram_id == 123456789
        assert contact.username == "john_doe"
        assert contact.display_name == "John Doe"
        assert len(contact.tags) == 2

    def test_contact_response_with_minimal_fields(self):
        """Test ContactResponse with minimal required fields."""
        now = datetime.now()
        contact = ContactResponse(
            id=1,
            telegram_id=123456789,
            username=None,
            first_name=None,
            last_name=None,
            display_name="Unknown User",
            phone=None,
            profile_photo_url=None,
            tags=[],
            updated_at=now,
        )

        assert contact.username is None
        assert len(contact.tags) == 0


class TestContactProfileResponse:
    """Tests for ContactProfileResponse schema."""

    def test_contact_profile_response_creation(self):
        """Test creating a valid ContactProfileResponse."""
        now = datetime.now()

        contact = ContactResponse(
            id=1,
            telegram_id=123456789,
            username="john_doe",
            first_name="John",
            last_name="Doe",
            display_name="John Doe",
            phone=None,
            profile_photo_url=None,
            tags=["Work"],
            updated_at=now,
        )

        tag = TagResponse(
            id=1, name="Work", color="#FF5733", created_at=now, contact_count=25
        )

        group = GroupInfo(
            id=1,
            telegram_id=1001234567890,
            name="Python Developers",
            member_count=150,
            profile_photo_url=None,
        )

        message = MessageInfo(id=1, content="Hello!", timestamp=now, is_outgoing=False)

        profile = ContactProfileResponse(
            contact=contact,
            tags=[tag],
            mutual_groups=[group],
            last_received_message=message,
            last_sent_message=None,
        )

        assert profile.contact.id == 1
        assert len(profile.tags) == 1
        assert len(profile.mutual_groups) == 1
        assert profile.last_received_message is not None
        assert profile.last_sent_message is None


class TestTagCreate:
    """Tests for TagCreate schema."""

    def test_tag_create_with_color(self):
        """Test creating a tag with color."""
        tag = TagCreate(name="Work", color="#FF5733")

        assert tag.name == "Work"
        assert tag.color == "#FF5733"

    def test_tag_create_without_color(self):
        """Test creating a tag without color."""
        tag = TagCreate(name="Personal", color=None)

        assert tag.name == "Personal"
        assert tag.color is None

    def test_tag_create_name_validation_empty(self):
        """Test that empty tag name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            TagCreate(name="", color=None)

        # Pydantic catches this before our validator runs
        assert "String should have at least 1 character" in str(exc_info.value)

    def test_tag_create_name_validation_whitespace(self):
        """Test that whitespace-only tag name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            TagCreate(name="   ", color=None)

        assert "Tag name cannot be empty" in str(exc_info.value)

    def test_tag_create_name_trimmed(self):
        """Test that tag name is trimmed."""
        tag = TagCreate(name="  Work  ", color=None)

        assert tag.name == "Work"

    def test_tag_create_color_validation_invalid(self):
        """Test that invalid color format raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            TagCreate(name="Work", color="FF5733")  # Missing #

        assert "valid hex color code" in str(exc_info.value)

    def test_tag_create_color_validation_invalid_chars(self):
        """Test that invalid hex characters raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            TagCreate(name="Work", color="#GG5733")

        assert "valid hex color code" in str(exc_info.value)

    def test_tag_create_color_validation_wrong_length(self):
        """Test that wrong length color raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            TagCreate(name="Work", color="#FF57")

        assert "valid hex color code" in str(exc_info.value)

    def test_tag_create_color_normalized_to_uppercase(self):
        """Test that color is normalized to uppercase."""
        tag = TagCreate(name="Work", color="#ff5733")

        assert tag.color == "#FF5733"

    def test_tag_create_name_too_long(self):
        """Test that name exceeding max length raises validation error."""
        with pytest.raises(ValidationError):
            TagCreate(name="A" * 51, color=None)


class TestTagUpdate:
    """Tests for TagUpdate schema."""

    def test_tag_update_name_only(self):
        """Test updating only name."""
        tag = TagUpdate(name="New Name", color=None)

        assert tag.name == "New Name"
        assert tag.color is None

    def test_tag_update_color_only(self):
        """Test updating only color."""
        tag = TagUpdate(name=None, color="#FF5733")

        assert tag.name is None
        assert tag.color == "#FF5733"

    def test_tag_update_both_fields(self):
        """Test updating both fields."""
        tag = TagUpdate(name="New Name", color="#FF5733")

        assert tag.name == "New Name"
        assert tag.color == "#FF5733"

    def test_tag_update_name_validation(self):
        """Test that empty name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            TagUpdate(name="   ", color=None)

        assert "Tag name cannot be empty" in str(exc_info.value)

    def test_tag_update_color_validation(self):
        """Test that invalid color raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            TagUpdate(name=None, color="invalid")

        assert "valid hex color code" in str(exc_info.value)


class TestTagResponse:
    """Tests for TagResponse schema."""

    def test_tag_response_creation(self):
        """Test creating a valid TagResponse."""
        now = datetime.now()
        tag = TagResponse(
            id=1, name="Work", color="#FF5733", created_at=now, contact_count=25
        )

        assert tag.id == 1
        assert tag.name == "Work"
        assert tag.color == "#FF5733"
        assert tag.created_at == now
        assert tag.contact_count == 25


class TestSendMessageRequest:
    """Tests for SendMessageRequest schema."""

    def test_send_message_request_creation(self):
        """Test creating a valid SendMessageRequest."""
        request = SendMessageRequest(contact_id=1, message="Hello, how are you?")

        assert request.contact_id == 1
        assert request.message == "Hello, how are you?"

    def test_send_message_request_contact_id_validation(self):
        """Test that contact_id must be positive."""
        with pytest.raises(ValidationError):
            SendMessageRequest(contact_id=0, message="Hello")

        with pytest.raises(ValidationError):
            SendMessageRequest(contact_id=-1, message="Hello")

    def test_send_message_request_message_validation_empty(self):
        """Test that empty message raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SendMessageRequest(contact_id=1, message="")

        # Pydantic catches this before our validator runs
        assert "String should have at least 1 character" in str(exc_info.value)

    def test_send_message_request_message_validation_whitespace(self):
        """Test that whitespace-only message raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            SendMessageRequest(contact_id=1, message="   ")

        assert "Message cannot be empty" in str(exc_info.value)

    def test_send_message_request_message_trimmed(self):
        """Test that message is trimmed."""
        request = SendMessageRequest(contact_id=1, message="  Hello  ")

        assert request.message == "Hello"

    def test_send_message_request_message_too_long(self):
        """Test that message exceeding Telegram limit raises validation error."""
        with pytest.raises(ValidationError):
            SendMessageRequest(contact_id=1, message="A" * 4097)


class TestBulkMessageRequest:
    """Tests for BulkMessageRequest schema."""

    def test_bulk_message_request_creation(self):
        """Test creating a valid BulkMessageRequest."""
        request = BulkMessageRequest(tag_ids=[1, 2, 3], message="Hello everyone!")

        assert request.tag_ids == [1, 2, 3]
        assert request.message == "Hello everyone!"

    def test_bulk_message_request_single_tag(self):
        """Test with single tag ID."""
        request = BulkMessageRequest(tag_ids=[1], message="Hello!")

        assert request.tag_ids == [1]

    def test_bulk_message_request_tag_ids_validation_empty(self):
        """Test that empty tag_ids raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            BulkMessageRequest(tag_ids=[], message="Hello")

        # Pydantic catches this before our validator runs
        assert "List should have at least 1 item" in str(exc_info.value)

    def test_bulk_message_request_tag_ids_validation_negative(self):
        """Test that negative tag ID raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            BulkMessageRequest(tag_ids=[1, -1], message="Hello")

        assert "Tag IDs must be positive" in str(exc_info.value)

    def test_bulk_message_request_tag_ids_validation_zero(self):
        """Test that zero tag ID raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            BulkMessageRequest(tag_ids=[0], message="Hello")

        assert "Tag IDs must be positive" in str(exc_info.value)

    def test_bulk_message_request_tag_ids_deduplication(self):
        """Test that duplicate tag IDs are removed."""
        request = BulkMessageRequest(tag_ids=[1, 2, 1, 3, 2], message="Hello")

        assert request.tag_ids == [1, 2, 3]

    def test_bulk_message_request_message_validation(self):
        """Test message validation."""
        with pytest.raises(ValidationError) as exc_info:
            BulkMessageRequest(tag_ids=[1], message="   ")

        assert "Message cannot be empty" in str(exc_info.value)


class TestMessageResult:
    """Tests for MessageResult schema."""

    def test_message_result_success(self):
        """Test creating a successful MessageResult."""
        result = MessageResult(
            contact_id=1,
            contact_name="John Doe",
            success=True,
            message_id=12345,
            error=None,
        )

        assert result.success is True
        assert result.message_id == 12345
        assert result.error is None

    def test_message_result_failure(self):
        """Test creating a failed MessageResult."""
        result = MessageResult(
            contact_id=1,
            contact_name="John Doe",
            success=False,
            message_id=None,
            error="User has blocked the bot",
        )

        assert result.success is False
        assert result.message_id is None
        assert result.error == "User has blocked the bot"


class TestBulkMessageJob:
    """Tests for BulkMessageJob schema."""

    def test_bulk_message_job_creation(self):
        """Test creating a valid BulkMessageJob."""
        now = datetime.now()
        job = BulkMessageJob(
            job_id="bulk_msg_20240101_120000_abc123",
            total_contacts=25,
            status="pending",
            started_at=now,
        )

        assert job.job_id == "bulk_msg_20240101_120000_abc123"
        assert job.total_contacts == 25
        assert job.status == "pending"
        assert job.started_at == now


class TestBulkMessageStatus:
    """Tests for BulkMessageStatus schema."""

    def test_bulk_message_status_in_progress(self):
        """Test creating a BulkMessageStatus for in-progress job."""
        now = datetime.now()
        status = BulkMessageStatus(
            job_id="bulk_msg_20240101_120000_abc123",
            total_contacts=25,
            sent=10,
            failed=0,
            in_progress=True,
            status="in_progress",
            started_at=now,
            completed_at=None,
            failures=[],
            message="Hello everyone!",
        )

        assert status.in_progress is True
        assert status.sent == 10
        assert status.failed == 0
        assert status.completed_at is None

    def test_bulk_message_status_completed(self):
        """Test creating a BulkMessageStatus for completed job."""
        now = datetime.now()
        completed = datetime.now()

        failure = MessageResult(
            contact_id=5,
            contact_name="Jane Doe",
            success=False,
            message_id=None,
            error="Network timeout",
        )

        status = BulkMessageStatus(
            job_id="bulk_msg_20240101_120000_abc123",
            total_contacts=25,
            sent=23,
            failed=2,
            in_progress=False,
            status="completed",
            started_at=now,
            completed_at=completed,
            failures=[failure],
            message="Hello everyone!",
        )

        assert status.in_progress is False
        assert status.sent == 23
        assert status.failed == 2
        assert status.completed_at is not None
        assert len(status.failures) == 1


class TestAuthInitRequest:
    """Tests for AuthInitRequest schema."""

    def test_auth_init_request_creation(self):
        """Test creating a valid AuthInitRequest."""
        request = AuthInitRequest(
            api_id=12345,
            api_hash="abcdef1234567890abcdef1234567890",
            phone="+1234567890",
        )

        assert request.api_id == 12345
        assert request.api_hash == "abcdef1234567890abcdef1234567890"
        assert request.phone == "+1234567890"

    def test_auth_init_request_api_id_validation(self):
        """Test that api_id must be positive."""
        with pytest.raises(ValidationError):
            AuthInitRequest(
                api_id=0,
                api_hash="abcdef1234567890abcdef1234567890",
                phone="+1234567890",
            )

    def test_auth_init_request_api_hash_validation_length(self):
        """Test that api_hash must be 32 characters."""
        with pytest.raises(ValidationError):
            AuthInitRequest(api_id=12345, api_hash="short", phone="+1234567890")

    def test_auth_init_request_api_hash_validation_format(self):
        """Test that api_hash must be hexadecimal."""
        with pytest.raises(ValidationError) as exc_info:
            AuthInitRequest(
                api_id=12345,
                api_hash="gggggggggggggggggggggggggggggggg",
                phone="+1234567890",
            )

        assert "32-character hexadecimal string" in str(exc_info.value)

    def test_auth_init_request_api_hash_normalized(self):
        """Test that api_hash is normalized to lowercase."""
        request = AuthInitRequest(
            api_id=12345,
            api_hash="ABCDEF1234567890ABCDEF1234567890",
            phone="+1234567890",
        )

        assert request.api_hash == "abcdef1234567890abcdef1234567890"

    def test_auth_init_request_phone_validation_no_plus(self):
        """Test that phone without + raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            AuthInitRequest(
                api_id=12345,
                api_hash="abcdef1234567890abcdef1234567890",
                phone="1234567890",
            )

        assert "must start with + and country code" in str(exc_info.value)

    def test_auth_init_request_phone_validation_invalid_format(self):
        """Test that invalid phone format raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            AuthInitRequest(
                api_id=12345,
                api_hash="abcdef1234567890abcdef1234567890",
                phone="+0123456789",  # Can't start with 0 after +
            )

        assert "Invalid phone number format" in str(exc_info.value)

    def test_auth_init_request_phone_trimmed(self):
        """Test that phone is trimmed and cleaned."""
        request = AuthInitRequest(
            api_id=12345,
            api_hash="abcdef1234567890abcdef1234567890",
            phone=" +1234567890 ",
        )

        assert request.phone == "+1234567890"

    def test_auth_init_request_phone_spaces_removed(self):
        """Test that spaces in phone are removed."""
        request = AuthInitRequest(
            api_id=12345,
            api_hash="abcdef1234567890abcdef1234567890",
            phone="+1 234 567 890",
        )

        assert request.phone == "+1234567890"


class TestAuthCodeRequest:
    """Tests for AuthCodeRequest schema."""

    def test_auth_code_request_creation(self):
        """Test creating a valid AuthCodeRequest."""
        request = AuthCodeRequest(phone="+1234567890", code="12345")

        assert request.phone == "+1234567890"
        assert request.code == "12345"

    def test_auth_code_request_code_validation_length(self):
        """Test that code must be 5-6 digits."""
        with pytest.raises(ValidationError):
            AuthCodeRequest(phone="+1234567890", code="123")

        with pytest.raises(ValidationError):
            AuthCodeRequest(phone="+1234567890", code="1234567")

    def test_auth_code_request_code_validation_format(self):
        """Test that code must be numeric."""
        with pytest.raises(ValidationError) as exc_info:
            AuthCodeRequest(phone="+1234567890", code="12a45")

        assert "must be 5-6 digits" in str(exc_info.value)

    def test_auth_code_request_code_six_digits(self):
        """Test that 6-digit code is valid."""
        request = AuthCodeRequest(phone="+1234567890", code="123456")

        assert request.code == "123456"

    def test_auth_code_request_phone_validation(self):
        """Test phone validation."""
        with pytest.raises(ValidationError):
            AuthCodeRequest(phone="1234567890", code="12345")


class TestAuthPasswordRequest:
    """Tests for AuthPasswordRequest schema."""

    def test_auth_password_request_creation(self):
        """Test creating a valid AuthPasswordRequest."""
        request = AuthPasswordRequest(password="MySecurePassword123")

        assert request.password == "MySecurePassword123"

    def test_auth_password_request_validation_empty(self):
        """Test that empty password raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            AuthPasswordRequest(password="")

        # Pydantic catches this before our validator runs
        assert "String should have at least 1 character" in str(exc_info.value)

    def test_auth_password_request_validation_whitespace(self):
        """Test that whitespace-only password raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            AuthPasswordRequest(password="   ")

        assert "Password cannot be empty" in str(exc_info.value)


class TestAuthResponse:
    """Tests for AuthResponse schema."""

    def test_auth_response_success(self):
        """Test creating a successful AuthResponse."""
        response = AuthResponse(
            success=True,
            requires_code=False,
            requires_password=False,
            message="Authentication successful",
            phone="+1234567890",
        )

        assert response.success is True
        assert response.requires_code is False
        assert response.requires_password is False
        assert response.phone == "+1234567890"

    def test_auth_response_requires_code(self):
        """Test AuthResponse requiring code."""
        response = AuthResponse(
            success=True,
            requires_code=True,
            requires_password=False,
            message="Verification code sent",
            phone="+1234567890",
        )

        assert response.requires_code is True

    def test_auth_response_requires_password(self):
        """Test AuthResponse requiring password."""
        response = AuthResponse(
            success=True,
            requires_code=False,
            requires_password=True,
            message="Please enter 2FA password",
            phone="+1234567890",
        )

        assert response.requires_password is True

    def test_auth_response_failure(self):
        """Test failed AuthResponse."""
        response = AuthResponse(
            success=False,
            requires_code=False,
            requires_password=False,
            message="Invalid credentials",
            phone=None,
        )

        assert response.success is False
        assert response.phone is None


class TestAuthStatusResponse:
    """Tests for AuthStatusResponse schema."""

    def test_auth_status_response_authenticated(self):
        """Test authenticated AuthStatusResponse."""
        response = AuthStatusResponse(
            authenticated=True,
            phone="+1234567890",
            session_valid=True,
            user_id=123456789,
            username="john_doe",
        )

        assert response.authenticated is True
        assert response.session_valid is True
        assert response.user_id == 123456789
        assert response.username == "john_doe"

    def test_auth_status_response_not_authenticated(self):
        """Test not authenticated AuthStatusResponse."""
        response = AuthStatusResponse(
            authenticated=False,
            phone=None,
            session_valid=False,
            user_id=None,
            username=None,
        )

        assert response.authenticated is False
        assert response.session_valid is False
        assert response.user_id is None
        assert response.username is None
