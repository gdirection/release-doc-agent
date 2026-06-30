from app.validation import validate_release_package


def test_validate_release_package_placeholder():
    result = validate_release_package({})
    assert result["valid"] is True
    assert result["issues"] == []
