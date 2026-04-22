from types import SimpleNamespace

import pytest

from kimi_cli.auth.platforms import get_platform_by_id
from kimi_cli.ui.shell import setup as shell_setup


@pytest.mark.asyncio
async def test_fallback_models_on_openai_404_prompts_manual_model(monkeypatch):
    platform = get_platform_by_id("alibaba-cloud-coding-plan")
    assert platform is not None

    answers = iter(["131072"])

    async def fake_prompt_choice(header: str, choices: list[str]) -> str:
        assert "qwen3-coder-plus" in choices
        return "qwen3-coder-plus"

    async def fake_prompt_text(prompt: str, **kwargs) -> str:
        return next(answers)

    monkeypatch.setattr(shell_setup, "_prompt_choice", fake_prompt_choice)
    monkeypatch.setattr(shell_setup, "_prompt_text", fake_prompt_text)

    error = SimpleNamespace(status=404)
    models = await shell_setup._fallback_models_on_list_error(platform, error)  # pyright: ignore[reportArgumentType]

    assert models is not None
    assert len(models) == 1
    assert models[0].id == "qwen3-coder-plus"
    assert models[0].context_length == 131072
