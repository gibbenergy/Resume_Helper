from types import SimpleNamespace
import gradio as gr


# ------------------------------------------------------------------
def create_experiences_tab(resume_helper):
    with gr.Tab("Experience") as tab:
        # ==================  INPUT FORM  ==================
        gr.Markdown("### Add Experience")

        with gr.Row():
            company_in  = gr.Textbox(label="Company",  interactive=True)
            position_in = gr.Textbox(label="Position", interactive=True)

        with gr.Row():
            location_in = gr.Textbox(label="Location",   interactive=True)
            start_in    = gr.Textbox(label="Start Date", interactive=True)
            end_in      = gr.Textbox(label="End Date",   interactive=True)

        desc_in = gr.Textbox(label="Description",  lines=3, interactive=True)
        achv_in = gr.Textbox(label="Achievements", lines=3, interactive=True)

        with gr.Row():
            add_btn   = gr.Button("➕ Add Experience", variant="primary")
            reset_btn = gr.Button("🔄 Reset Form")

        # ==================  HISTORY TABLE  ===============
        gr.Markdown("---\n### Experience History")

        work_df = gr.Dataframe(
            headers=[
                "Company", "Position", "Location",
                "Start", "End", "Description", "Achievements",
            ],
            datatype=["str"] * 7,
            type="array",
            col_count=(7, "fixed"),
            row_count=10,
            interactive=True,
            value=[],
            show_row_numbers=True,     # makes selection obvious
            label="Experience History",
        )

        with gr.Row():
            move_up_btn    = gr.Button("⬆️ Move Up")
            move_down_btn  = gr.Button("⬇️ Move Down")
            remove_btn     = gr.Button("🗑️ Remove Selected", variant="secondary")
            clear_btn      = gr.Button("❌ Clear All",        variant="secondary")

        # ==================  STATE  ========================
        selected_idx = gr.State(None)     # remembers clicked row

        # ==================  CALLBACKS =====================
        # --- reset form ---
        reset_btn.click(
            resume_helper.reset_work_experience,
            None,
            [
                company_in, position_in, location_in,
                start_in,   end_in,     desc_in, achv_in,
            ],
        )

        # --- add row ---
        add_btn.click(
            resume_helper.add_work_experience,
            [
                company_in, position_in, location_in,
                start_in,   end_in,     desc_in, achv_in,
                work_df,
            ],
            work_df,
        )

        # --- capture row click ---
        def _capture_row(evt: gr.SelectData):
            # evt.index is (row, col) tuple in 5.24
            idx = evt.index
            if idx is None:
                return None
            return idx[0] if isinstance(idx, (list, tuple)) else int(idx)

        work_df.select(_capture_row, None, selected_idx)

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
            [work_df, selected_idx],
            [work_df, selected_idx],
        )

        move_up_btn.click(
            _move_up,
            [work_df, selected_idx],
            [work_df, selected_idx],
        )

        move_down_btn.click(
            _move_down,
            [work_df, selected_idx],
            [work_df, selected_idx],
        )

        clear_btn.click(
            resume_helper.clear_work_experience,
            None,
            work_df,
        )

    # ==================  EXPORT  ==========================
    components = {
        "company_input":        company_in,
        "position_input":       position_in,
        "work_location_input":  location_in,
        "work_start_input":     start_in,
        "work_end_input":       end_in,
        "work_desc_input":      desc_in,
        "achievements_input":   achv_in,
        "work_list":            work_df,
    }
    return SimpleNamespace(tab=tab, components=components)
