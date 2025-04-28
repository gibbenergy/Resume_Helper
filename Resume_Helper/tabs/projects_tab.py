from types import SimpleNamespace
import gradio as gr


# ------------------------------------------------------------------
def create_projects_tab(resume_helper):
    with gr.Tab("Projects") as tab:
        # ==================  INPUT FORM  ==================
        gr.Markdown("### Add Project")

        with gr.Row():
            title_in = gr.Textbox(label="Project Title", interactive=True)
            url_in = gr.Textbox(label="URL", interactive=True)

        with gr.Row():
            start_in = gr.Textbox(label="Start Date", interactive=True)
            end_in = gr.Textbox(label="End Date", interactive=True)

        desc_in = gr.Textbox(label="Description", lines=3, interactive=True)
        tech_in = gr.Textbox(label="Technologies", interactive=True)

        with gr.Row():
            add_btn = gr.Button("➕ Add Project", variant="primary")
            reset_btn = gr.Button("🔄 Reset Form")

        # ==================  HISTORY TABLE  ===============
        gr.Markdown("---\n### Projects List")

        project_df = gr.Dataframe(
            headers=["Title", "Description", "Technologies", "URL", "Start", "End"],
            datatype=["str"] * 6,
            type="array",
            col_count=(6, "fixed"),
            row_count=10,
            interactive=True,
            value=[],
            show_row_numbers=True,     # makes selection obvious
            label="Projects List",
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
            resume_helper.reset_projects,
            None,
            [title_in, desc_in, tech_in, url_in, start_in, end_in],
        )

        # --- add row ---
        add_btn.click(
            resume_helper.add_project,
            [title_in, desc_in, tech_in, url_in, start_in, end_in, project_df],
            project_df,
        )

        # --- capture row click ---
        def _capture_row(evt: gr.SelectData):
            # evt.index is (row, col) tuple in 5.24
            idx = evt.index
            if idx is None:
                return None
            return idx[0] if isinstance(idx, (list, tuple)) else int(idx)

        project_df.select(_capture_row, None, selected_idx)

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
            [project_df, selected_idx],
            [project_df, selected_idx],
        )

        move_up_btn.click(
            _move_up,
            [project_df, selected_idx],
            [project_df, selected_idx],
        )

        move_down_btn.click(
            _move_down,
            [project_df, selected_idx],
            [project_df, selected_idx],
        )

        clear_btn.click(
            resume_helper.clear_projects,
            None,
            project_df,
        )

    # ==================  EXPORT  ==========================
    components = {
        "project_title_input": title_in,
        "project_desc_input": desc_in,
        "project_tech_input": tech_in,
        "project_url_input": url_in,
        "project_start_input": start_in,
        "project_end_input": end_in,
        "project_list": project_df,
        "selected_project_idx": selected_idx
    }
    return SimpleNamespace(tab=tab, components=components)
