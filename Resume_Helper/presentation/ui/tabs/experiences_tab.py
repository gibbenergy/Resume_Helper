from types import SimpleNamespace
import gradio as gr


def create_experiences_tab(resume_helper):
    with gr.Tab("Experience") as tab:
        gr.Markdown("### Add Experience")

        with gr.Row():
            company_in  = gr.Textbox(label="Company",  lines=2, interactive=True)
            position_in = gr.Textbox(label="Position", lines=2, interactive=True)

        with gr.Row():
            location_in = gr.Textbox(label="Location",   lines=2, interactive=True)
            start_in    = gr.Textbox(label="Start Date", lines=2, interactive=True)
            end_in      = gr.Textbox(label="End Date",   lines=2, interactive=True)

        desc_in = gr.Textbox(label="Description",  lines=3, interactive=True)
        achv_in = gr.Textbox(label="Achievements", lines=3, interactive=True)

        with gr.Row():
            add_btn   = gr.Button("➕ Add Experience", variant="primary")
            reset_btn = gr.Button("🔄 Reset Form")

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
            show_row_numbers=True,
            label="Experience History",
        )

        with gr.Row():
            move_up_btn    = gr.Button("⬆️ Move Up")
            move_down_btn  = gr.Button("⬇️ Move Down")
            remove_btn     = gr.Button("🗑️ Remove Selected", variant="secondary")
            clear_btn      = gr.Button("❌ Clear All",        variant="secondary")

        selected_idx = gr.State(None)

        reset_btn.click(
            resume_helper.reset_experience,
            None,
            [
                company_in, position_in, location_in,
                start_in,   end_in,     desc_in, achv_in,
            ],
        )

        add_btn.click(
            resume_helper.add_experience,
            [
                company_in, position_in, location_in,
                start_in,   end_in,     desc_in, achv_in,
                work_df,
            ],
            work_df,
        )

        def _capture_row(evt: gr.SelectData):
            idx = evt.index
            if idx is None:
                return None
            return idx[0] if isinstance(idx, (list, tuple)) else int(idx)

        work_df.select(_capture_row, None, selected_idx)

        def _remove_row(table, idx):
            if idx is None or not 0 <= idx < len(table):
                return table, None
            tbl = table.copy()
            tbl.pop(idx)
            return tbl, None

        def _move_up(table, idx):
            if idx is None or idx <= 0 or idx >= len(table):
                return table, idx
            tbl = table.copy()
            tbl[idx - 1], tbl[idx] = tbl[idx], tbl[idx - 1]
            return tbl, idx - 1

        def _move_down(table, idx):
            if idx is None or idx < 0 or idx >= len(table) - 1:
                return table, idx
            tbl = table.copy()
            tbl[idx + 1], tbl[idx] = tbl[idx], tbl[idx + 1]
            return tbl, idx + 1

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
            resume_helper.clear_experience,
            None,
            work_df,
        )

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
