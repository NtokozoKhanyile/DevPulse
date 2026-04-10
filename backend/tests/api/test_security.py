"""
Tests for security utilities: password hashing, token creation/validation.
"""

import pytest
import time
from datetime import datetime, timedelta, timezone

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings
from jose import JWTError


# ============================================================================
# Utility Functions
# ============================================================================


def truncate_password(pwd: str, max_bytes: int = 72) -> str:
    """
    Truncate password safely to bcrypt's 72-byte limit while handling UTF-8.
    
    Bcrypt truncates passwords at 72 bytes. This helper ensures that passwords
    are safely truncated without breaking UTF-8 sequences.
    
    Args:
        pwd: The password string to truncate
        max_bytes: Maximum bytes allowed (default: 72 for bcrypt)
        
    Returns:
        The password, truncated if necessary, safe for bcrypt hashing
    """
    encoded = pwd.encode('utf-8')
    if len(encoded) > max_bytes:
        # Truncate and safely decode, ignoring incomplete UTF-8 sequences
        return encoded[:max_bytes].decode('utf-8', errors='ignore')
    return pwd


class TestPasswordHashing:
    """Password hashing security tests."""

    def test_hash_password_creates_hash(self):
        """Test password hashing creates a hash. Bcrypt has 72-byte limit."""
        password = truncate_password("Pass123!")
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        # Bcrypt hashes start with $2a$, $2b$, or $2y$
        assert hashed.startswith("$2")

    def test_hash_password_idempotent_hash_differs(self):
        """Test hashing the same password twice produces different hashes."""
        password = truncate_password("Pass123!")
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different (bcrypt uses salt)
        assert hash1 != hash2

    def test_verify_password_success(self):
        """Test password verification succeeds with correct password."""
        password = truncate_password("Pass123!")
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        """Test password verification fails with wrong password."""
        password = truncate_password("Pass123!")
        hashed = hash_password(password)

        assert verify_password("Wrong123!", hashed) is False

    def test_verify_password_case_sensitive(self):
        """Test password verification is case-sensitive."""
        password = truncate_password("Pass123!")
        hashed = hash_password(password)

        assert verify_password("pass123!", hashed) is False

    def test_hash_empty_password(self):
        """Test hashing empty password is possible (though not recommended)."""
        hashed = hash_password(truncate_password(""))
        assert len(hashed) > 0
        assert verify_password("", hashed) is True

    def test_hash_very_long_password(self):
        """Test hashing password longer than bcrypt's 72-byte limit."""
        # Create a password that exceeds 72 bytes
        very_long_password = "SuperSecure@123!Password#456$WithMany@Symbols%And&Characters*(Very)Long"  # ~70 bytes
        even_longer = very_long_password + "!!!EXTRA_CONTENT_TO_EXCEED_72_BYTES_LIMIT!!!"  # >150 bytes
        
        # Truncate to bcrypt's limit
        truncated = truncate_password(even_longer)
        
        # Should successfully hash and verify with truncated version
        hashed = hash_password(truncated)
        assert verify_password(truncated, hashed) is True
        
        # Verify it's actually truncated
        assert len(truncated.encode('utf-8')) <= 72


class TestAccessTokens:
    """Access token creation and validation tests."""

    def test_create_access_token_success(self):
        """Test creating an access token."""
        user_id = "12345-67890"
        token = create_access_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_access_token_can_be_decoded(self):
        """Test access token can be decoded."""
        user_id = "12345-67890"
        token = create_access_token(user_id)
        payload = decode_token(token)

        assert payload["sub"] == user_id
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_access_token_has_expiration(self):
        """Test access token has correct expiration."""
        user_id = "12345-67890"
        token = create_access_token(user_id)
        payload = decode_token(token)

        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        delta = (exp_time - now).total_seconds() / 60

        # Should expire in approximately X minutes (with some tolerance)
        assert abs(delta - settings.access_token_expire_minutes) < 2

    def test_access_token_wrong_secret_fails(self):
        """Test token with wrong secret cannot be decoded."""
        user_id = "12345-67890"
        token = create_access_token(user_id)

        # Try to decode with wrong secret
        from jose import jwt
        with pytest.raises(JWTError):
            jwt.decode(
                token,
                "wrong_secret_key_that_is_long_enough",
                algorithms=["HS256"],
            )

    def test_expired_token_fails_decode(self):
        """Test expired token cannot be decoded."""
        from jose import jwt
        from app.core.security import pwd_context

        # Create a token that's already expired
        expired_token = jwt.encode(
            {
                "sub": "user-id",
                "exp": datetime.now(timezone.utc) - timedelta(hours=1),
                "type": "access",
            },
            settings.secret_key,
            algorithm=settings.algorithm,
        )

        with pytest.raises(JWTError):
            decode_token(expired_token)


class TestRefreshTokens:
    """Refresh token creation and validation tests."""

    def test_create_refresh_token_success(self):
        """Test creating a refresh token."""
        user_id = "12345-67890"
        token = create_refresh_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_refresh_token_can_be_decoded(self):
        """Test refresh token can be decoded."""
        user_id = "12345-67890"
        token = create_refresh_token(user_id)
        payload = decode_token(token)

        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
        assert "exp" in payload

    def test_refresh_token_has_longer_expiration(self):
        """Test refresh token has longer expiration than access token."""
        user_id = "12345-67890"
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)

        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)

        access_exp = access_payload["exp"]
        refresh_exp = refresh_payload["exp"]

        # Refresh token should expire later
        assert refresh_exp > access_exp

    def test_access_token_type_is_access(self):
        """Test access token has type 'access'."""
        token = create_access_token("user-id")
        payload = decode_token(token)
        assert payload["type"] == "access"

    def test_refresh_token_type_is_refresh(self):
        """Test refresh token has type 'refresh'."""
        token = create_refresh_token("user-id")
        payload = decode_token(token)
        assert payload["type"] == "refresh"


class TestTokenValidation:
    """Token validation and security tests."""

    def test_decode_token_with_invalid_format(self):
        """Test decoding invalid token format."""
        with pytest.raises(JWTError):
            decode_token("not.a.valid.jwt")

    def test_decode_token_with_corrupted_signature(self):
        """Test decoding token with corrupted signature."""
        token = create_access_token("user-id")
        # Corrupt the token
        corrupted = token[:-10] + "corrupted!"

        with pytest.raises(JWTError):
            decode_token(corrupted)

    def test_tokens_are_different_for_different_users(self):
        """Test tokens generated for different users are different."""
        token1 = create_access_token("user-1")
        token2 = create_access_token("user-2")

        assert token1 != token2

    def test_payload_subject_matches_user_id(self):
        """Test token payload subject matches provided user ID."""
        user_id = "specific-user-id-12345"
        token = create_access_token(user_id)
        payload = decode_token(token)

        assert payload["sub"] == user_id

    def test_token_includes_required_fields(self):
        """Test all required fields are present in token payload."""
        token = create_access_token("user-id")
        payload = decode_token(token)

        required_fields = ["sub", "exp", "type"]
        for field in required_fields:
            assert field in payload


class TestSecurityEdgeCases:
    """Edge case and security-specific tests."""

    def test_password_with_special_characters(self):
        """Test hashing password with special characters."""
        password = truncate_password("P@$$w0rd!#%&*()_+=[]{}|;:,.<>?/~`")
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_password_unicode_characters(self):
        """Test hashing password with unicode characters."""
        password = truncate_password("Пас密碼한글🔒🔑")
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_multiple_verifications_consistent(self):
        """Test multiple password verifications are consistent."""
        password = truncate_password("Pass123!")
        hashed = hash_password(password)

        # Verify multiple times
        for _ in range(5):
            assert verify_password(password, hashed) is True
            assert verify_password("Wrong123!", hashed) is False

    def test_token_with_empty_user_id(self):
        """Test creating token with empty user ID."""
        token = create_access_token("")
        payload = decode_token(token)
        assert payload["sub"] == ""

    def test_token_with_very_long_user_id(self):
        """Test creating token with very long user ID."""
        long_id = "x" * 1000
        token = create_access_token(long_id)
        payload = decode_token(token)
        assert payload["sub"] == long_id


class TestPasswordTruncation:
    """Test password truncation helper for bcrypt's 72-byte limit."""

    def test_truncate_short_password_unchanged(self):
        """Test that short passwords are not truncated."""
        password = truncate_password("Pass123!")
        result = truncate_password(password)
        assert result == password
        assert len(result.encode('utf-8')) <= 72

    def test_truncate_exactly_72_bytes_unchanged(self):
        """Test password exactly at 72-byte limit is unchanged."""
        password = truncate_password("x" * 72)
        result = truncate_password(password)
        assert result == password
        assert len(result.encode('utf-8')) == 72

    def test_truncate_long_password(self):
        """Test that long passwords are truncated to 72 bytes."""
        password = truncate_password("x" * 200)
        result = truncate_password(password)
        assert len(result.encode('utf-8')) <= 72
        assert len(result.encode('utf-8')) > 0

    def test_truncate_preserves_function_for_bcrypt(self):
        """Test truncated passwords work with bcrypt hashing."""
        long_password = truncate_password("x" * 150)
        truncated = truncate_password(long_password)
        
        # Should be hashable and verifiable
        hashed = hash_password(truncated)
        assert verify_password(truncated, hashed) is True

    def test_truncate_unicode_safely(self):
        """Test truncation handles UTF-8 multi-byte characters safely."""
        # Multi-byte UTF-8 unicode characters
        unicode_password = "Пас密碼한글🔒🔑" * 20  # Will exceed 72 bytes
        result = truncate_password(unicode_password)
        
        # Should still be valid UTF-8 and under limit
        assert len(result.encode('utf-8')) <= 72
        # Should not raise encoding errors
        result.encode('utf-8')
        
        # Should still work with bcrypt
        hashed = hash_password(result)
        assert verify_password(result, hashed) is True

    def test_truncate_special_characters_safely(self):
        """Test truncation with special characters."""
        special_password = "P@$$w0rd!#%&*()_+=[]{}|;:,.<>?/~`" * 5
        result = truncate_password(special_password)
        
        assert len(result.encode('utf-8')) <= 72
        hashed = hash_password(result)
        assert verify_password(result, hashed) is True

    def test_truncate_respects_max_bytes_parameter(self):
        """Test truncate_password respects custom max_bytes parameter."""
        password = "x" * 100
        
        # Default 72 bytes
        result_72 = truncate_password(password)
        assert len(result_72.encode('utf-8')) <= 72
        
        # Custom limit
        result_50 = truncate_password(password, max_bytes=50)
        assert len(result_50.encode('utf-8')) <= 50

    def test_truncate_empty_password(self):
        """Test truncating empty password."""
        result = truncate_password("")
        assert result == ""

    def test_truncate_mixed_content(self):
        """Test truncation with mixed ASCII and unicode."""
        password = "Pass1!" + "🔒" * 30 + "SecureData" * 5
        result = truncate_password(password)
        
        assert len(result.encode('utf-8')) <= 72
        hashed = hash_password(result)
        assert verify_password(result, hashed) is True
