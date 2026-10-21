from masking import mask, mask_messages


def test_masks_known_keys():
    text, found = mask("klucz sk-or-v1-" + "a" * 40 + " i AKIAABCDEFGHIJKLMNOP oraz glpat-" + "x" * 20)
    assert "sk-or-v1" not in text and "AKIA" not in text and "glpat" not in text
    assert found == ["openrouter_key", "aws_access_key", "gitlab_token"]


def test_masks_only_value_of_assignment():
    text, found = mask('DB_PASSWORD="hunter2secret"')
    assert text == 'DB_PASSWORD="[MASKED:password]"'
    assert found == ["password"]


def test_mask_messages_handles_text_parts():
    msgs, found = mask_messages([
        {"role": "user", "content": [{"type": "text", "text": "token: abcdef123456"}]},
        {"role": "tool", "content": "Bearer " + "z" * 30},
    ])
    assert msgs[0]["content"][0]["text"] == "token: [MASKED:password]"
    assert msgs[1]["content"] == "Bearer [MASKED:bearer]"
    assert found == ["password", "bearer"]
