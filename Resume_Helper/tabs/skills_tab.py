from types import SimpleNamespace
import gradio as gr


# ------------------------------------------------------------------
def create_skills_tab(resume_helper):
    with gr.Tab("Skills") as tab:
        # ==================  INPUT FORM  ==================
        gr.Markdown("### Add Skill")

        with gr.Row():
            category_in = gr.Textbox(label="Category", interactive=True)
            skill_name_in = gr.Textbox(label="Skill Name", interactive=True)
            proficiency_in = gr.Textbox(label="Proficiency", interactive=True)

        with gr.Row():
            add_btn = gr.Button("➕ Add Skill", variant="primary")
            reset_btn = gr.Button("🔄 Reset Form")

        # ==================  HISTORY TABLE  ===============
        gr.Markdown("---\n### Skills List")

        skill_df = gr.Dataframe(
            headers=["Category", "Skill Name", "Proficiency"],
            datatype=["str"] * 3,
            type="array",
            col_count=(3, "fixed"),
            row_count=10,
            interactive=True,
            value=[],
            show_row_numbers=True,     # makes selection obvious
            label="Skills List",
        )

        with gr.Row():
            move_up_btn = gr.Button("⬆️ Move Up")
            move_down_btn = gr.Button("⬇️ Move Down")
            remove_btn = gr.Button("🗑️ Remove Selected", variant="secondary")
            clear_btn = gr.Button("❌ Clear All", variant="secondary")

        # ==================  STATE  ========================
        selected_idx = gr.State(None)     # remembers clicked row

        # ==================  CALLBACKS =====================
        # --- reset form ---
        reset_btn.click(
            resume_helper.reset_skills,
            None,
            [category_in, skill_name_in, proficiency_in],
        )

        # --- add row ---
        add_btn.click(
            resume_helper.add_skill,
            [category_in, skill_name_in, proficiency_in, skill_df],
            skill_df,
        )

        # --- capture row click ---
        def _capture_row(evt: gr.SelectData):
            # evt.index is (row, col) tuple in 5.24
            idx = evt.index
            if idx is None:
                return None
            return idx[0] if isinstance(idx, (list, tuple)) else int(idx)

        skill_df.select(_capture_row, None, selected_idx)

        # ------------- helpers that modify the table --------------
        def _remove_row(table, idx):
            if idx is None or not 0 <= idx < len(table):
                return table, None
            tbl = table.copy()
            tbl.pop(idx)
            return tbl, None  # clear selection afterwards

        def _move_up(table, idx):
            if idx is None or idx <= 0 or idx >= len(table):
                return table, idx  # nothing happens
            tbl = table.copy()
            tbl[idx - 1], tbl[idx] = tbl[idx], tbl[idx - 1]
            return tbl, idx - 1    # new selection one row higher

        def _move_down(table, idx):
            if idx is None or idx < 0 or idx >= len(table) - 1:
                return table, idx  # nothing happens
            tbl = table.copy()
            tbl[idx + 1], tbl[idx] = tbl[idx], tbl[idx + 1]
            return tbl, idx + 1    # new selection one row lower

        # --- wire buttons ---
        remove_btn.click(
            _remove_row,
            [skill_df, selected_idx],
            [skill_df, selected_idx],
        )

        move_up_btn.click(
            _move_up,
            [skill_df, selected_idx],
            [skill_df, selected_idx],
        )

        move_down_btn.click(
            _move_down,
            [skill_df, selected_idx],
            [skill_df, selected_idx],
        )

        clear_btn.click(
            resume_helper.clear_skills,
            None,
            skill_df,
        )

    # ==================  EXPORT  ==========================
    components = {
        "category_input": category_in,
        "skill_input": skill_name_in,
        "proficiency_input": proficiency_in,
        "skill_list": skill_df,
        "selected_skill_idx": selected_idx
    }
    return SimpleNamespace(tab=tab, components=components)
