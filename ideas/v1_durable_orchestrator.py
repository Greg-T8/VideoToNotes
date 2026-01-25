import azure.functions as func
import azure.durable_functions as df

# Orchestrator: Two-stage processing
@df.orchestrator_trigger(context_name="context")
def orchestrate_exam_notes(context: df.DurableOrchestrationContext):
    input_data = context.get_input()
    toc_hierarchy = input_data["toc_hierarchy"]
    chunk_blob_urls = input_data["chunk_blob_urls"]
    
    # ═══════════════════════════════════════════════════════════
    # STAGE 1: Process chunks in parallel (fan-out)
    # ═══════════════════════════════════════════════════════════
    chunk_tasks = []
    for i, chunk_url in enumerate(chunk_blob_urls):
        task = context.call_activity("process_chunk", {
            "chunk_id": i + 1,
            "total_chunks": len(chunk_blob_urls),
            "chunk_url": chunk_url,
            "toc_hierarchy": toc_hierarchy
        })
        chunk_tasks.append(task)
    
    # Wait for all chunks to complete
    chunk_notes = yield context.task_all(chunk_tasks)
    # chunk_notes = [{"sections": {"Section A": "...", "Section B": "..."}}, ...]
    
    # ═══════════════════════════════════════════════════════════
    # STAGE 2: Group by section, merge in parallel (fan-out)
    # ═══════════════════════════════════════════════════════════
    section_partials = group_notes_by_section(chunk_notes)
    # section_partials = {"Section A": [part1, part2], "Section B": [part1], ...}
    
    merge_tasks = []
    for section_title, partials in section_partials.items():
        if len(partials) == 1:
            # No merge needed, single source
            merge_tasks.append(context.call_activity("passthrough", {
                "section_title": section_title,
                "content": partials[0]
            }))
        else:
            # Multiple partials, need AI merge
            merge_tasks.append(context.call_activity("merge_section", {
                "section_title": section_title,
                "partials": partials
            }))
    
    merged_sections = yield context.task_all(merge_tasks)
    # merged_sections = [{"title": "Section A", "content": "..."}, ...]
    
    # ═══════════════════════════════════════════════════════════
    # STAGE 3: Assemble final document (deterministic, no AI)
    # ═══════════════════════════════════════════════════════════
    final_doc = yield context.call_activity("assemble_document", {
        "toc_hierarchy": toc_hierarchy,
        "merged_sections": {s["title"]: s["content"] for s in merged_sections}
    })
    
    return final_doc  # URL to final markdown file


def group_notes_by_section(chunk_notes: list) -> dict:
    """Group all partial notes by section title."""
    section_partials = {}
    for chunk_result in chunk_notes:
        for section_title, content in chunk_result["sections"].items():
            if section_title not in section_partials:
                section_partials[section_title] = []
            section_partials[section_title].append(content)
    return section_partials