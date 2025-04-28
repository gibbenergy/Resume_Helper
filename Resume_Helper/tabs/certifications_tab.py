from types import SimpleNamespace
import gradio as gr


# ------------------------------------------------------------------
def create_certifications_tab(resume_helper):
    with gr.Tab("Certifications") as tab:
        # ==================  INPUT FORM  ==================
        gr.Markdown("### Add Certification")

        with gr.Row():
            cert_name_in = gr.Textbox(label="Certification Name", interactive=True)
            cert_issuer_in = gr.Textbox(label="Issuer", interactive=True)

        with gr.Row():
            cert_date_in = gr.Textbox(label="Date Obtained", interactive=True)
            cert_id_in = gr.Textbox(label="Credential ID", interactive=True)
            cert_url_in = gr.Textbox(label="URL", interactive=True)

        with gr.Row():
            add_btn = gr.Button("➕ Add Certification", variant="primary")
            reset_btn = gr.Button("🔄 Reset Form")

        # ==================  HISTORY TABLE  ===============
        gr.Markdown("---\n### Certifications List")

        cert_df = gr.Dataframe(
            headers=["Name", "Issuer", "Date", "Credential ID", "URL"],
            datatype=["str"] * 5,
            type="array",
            col_count=(5, "fixed"),
            row_count=10,
            interactive=True,
            value=[],
            show_row_numbers=True,     # makes selection obvious
            label="Certifications List",
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
            resume_helper.reset_certifications,
            None,
            [cert_name_in, cert_issuer_in, cert_date_in, cert_id_in, cert_url_in],
        )

        # --- add row ---
        add_btn.click(
            resume_helper.add_certification,
            [cert_name_in, cert_issuer_in, cert_date_in, cert_id_in, cert_url_in, cert_df],
            cert_df,
        )

        # --- capture row click ---
        def _capture_row(evt: gr.SelectData):
            # evt.index is (row, col) tuple in 5.24
            idx = evt.index
            if idx is None:
                return None
            return idx[0] if isinstance(idx, (list, tuple)) else int(idx)

        cert_df.select(_capture_row, None, selected_idx)

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
            [cert_df, selected_idx],
            [cert_df, selected_idx],
        )

        move_up_btn.click(
            _move_up,
            [cert_df, selected_idx],
            [cert_df, selected_idx],
        )

        move_down_btn.click(
            _move_down,
            [cert_df, selected_idx],
            [cert_df, selected_idx],
        )

        clear_btn.click(
            resume_helper.clear_certifications,
            None,
            cert_df,
        )

    # ==================  EXPORT  ==========================
    components = {
        "cert_name_input": cert_name_in,
        "cert_issuer_input": cert_issuer_in,
        "cert_date_input": cert_date_in,
        "cert_id_input": cert_id_in,
        "cert_url_input": cert_url_in,
        "cert_list": cert_df,
        "selected_cert_idx": selected_idx
    }
    return SimpleNamespace(tab=tab, components=components)
