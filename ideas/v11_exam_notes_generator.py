async def generate_notes(
    contents_path: str,
    zip_path: str,
    output_path: str,
    prompts_dir: Path,
    stage1_model: str = "openai/gpt-4.1-mini",
    stage2_model: str = "deepseek/deepseek-r1-0528"
):
    """Main pipeline."""
    
    print(f"🤖 Models: Stage1={stage1_model}, Stage2={stage2_model}")
    print(f"📝 Prompts: {prompts_dir}")
    
    # ... rest of function uses stage1_model and stage2_model instead of constants