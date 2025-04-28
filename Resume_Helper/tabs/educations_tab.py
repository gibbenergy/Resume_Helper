from types import SimpleNamespace
import gradio as gr


# ------------------------------------------------------------------
def create_educations_tab(resume_helper):
    with gr.Tab("Education") as tab:
        # ==================  INPUT FORM  ==================
        gr.Markdown("### Add Education")

        with gr.Row():
            institution_in = gr.Textbox(label="Institution", interactive=True)
            degree_in = gr.Textbox(label="Degree", interactive=True)

        with gr.Row():
            field_in = gr.Textbox(label="Field of Study", interactive=True)
            gpa_in = gr.Textbox(label="GPA", interactive=True)

        with gr.Row():
            start_in = gr.Textbox(label="Start Date", interactive=True)
            end_in = gr.Textbox(label="End Date", interactive=True)

        desc_in = gr.Textbox(label="Description", lines=3, interactive=True)

        with gr.Row():
            add_btn = gr.Button("➕ Add Education", variant="primary")
            reset_btn = gr.Button("🔄 Reset Form")

        # ==================  HISTORY TABLE  ===============
        gr.Markdown("---\n### Education History")

        edu_df = gr.Dataframe(
            headers=[
                "Institution", "Degree", "Field", "GPA", 
                "Start", "End", "Description"
            ],
            datatype=["str"] * 7,
            type="array",
            col_count=(7, "fixed"),
            row_count=10,
            interactive=True,
            value=[],
            show_row_numbers=True,     # makes selection obvious
            label="Education History",
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
            resume_helper.reset_education,
            None,
            [
                institution_in, degree_in, field_in,
                gpa_in, start_in, end_in, desc_in,
            ],
        )

        # --- add row ---
        add_btn.click(
            resume_helper.add_education,
            [
                institution_in, degree_in, field_in,
                start_in, end_in, gpa_in, desc_in,
                edu_df,
            ],
            edu_df,
        )

        # --- capture row click ---
        def _capture_row(evt: gr.SelectData):
            # evt.index is (row, col) tuple in 5.24
            idx = evt.index
            if idx is None:
                return None
            return idx[0] if isinstance(idx, (list, tuple)) else int(idx)

        edu_df.select(_capture_row, None, selected_idx)

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
            [edu_df, selected_idx],
            [edu_df, selected_idx],
        )

        move_up_btn.click(
            _move_up,
            [edu_df, selected_idx],
            [edu_df, selected_idx],
        )

        move_down_btn.click(
            _move_down,
            [edu_df, selected_idx],
            [edu_df, selected_idx],
        )

        clear_btn.click(
            resume_helper.clear_education,
            None,
            edu_df,
        )

    # ==================  EXPORT  ==========================
    components = {
        "institution_input": institution_in,
        "degree_input": degree_in,
        "field_input": field_in,
        "gpa_input": gpa_in,
        "edu_start_input": start_in,
        "edu_end_input": end_in,
        "edu_desc_input": desc_in,
        "edu_list": edu_df,
        "selected_edu_idx": selected_idx
    }
    return SimpleNamespace(tab=tab, components=components)
