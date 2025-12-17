from types import SimpleNamespace
import gradio as gr
def wrap_text(text, max_length=50):
    """Insert line breaks in long text for better display in tables."""
    if not text or len(text) <= max_length:
        return text
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        word_length = len(word)
        if current_length + word_length + len(current_line) > max_length:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length
            else:
                lines.append(word)
                current_length = 0
        else:
            current_line.append(word)
            current_length += word_length
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines)


def generate_table_from_sections(sections_dict):
    """Generate table data from sections dictionary."""
    table_data = []
    for section_name, items in sections_dict.items():
        for item in items:
            table_data.append([
                section_name,
                item["title"],
                item["organization"],
                item["date"],
                item["location"],
                item["description"],
                item["url"]
            ])
    return table_data
COMMON_SECTIONS = [
    "Awards & Honors",
    "Publications", 
    "Volunteer Work",
    "Professional Memberships",
    "Conferences & Events",
    "Languages",
    "Hobbies & Interests",
    "Additional Information",
    "References",
    "Patents",
    "Speaking Engagements",
    "Community Involvement",
    "➕ Create New Section..."
]
def create_others_tab(resume_helper):
    with gr.Tab("Others") as tab:
        gr.Markdown("---\n### ➕ Add Item to Section")
        
        with gr.Row():
            section_selector = gr.Dropdown(
                label="Select Section",
                choices=COMMON_SECTIONS,
                value=COMMON_SECTIONS[0] if COMMON_SECTIONS else None,
                interactive=True,
                scale=2,
                info="Choose from common sections or select 'Create New Section...' to add a custom one"
            )
        with gr.Row(visible=False) as custom_section_row:
            custom_section_input = gr.Textbox(
                label="New Section Name", 
                placeholder="e.g., Research Projects, Military Service, Licenses",
                lines=2,
                interactive=True,
                scale=2
            )
            create_section_btn = gr.Button("➕ Create", variant="primary", scale=1)
            
        with gr.Row():
            item_title = gr.Textbox(
                label="Title/Name", 
                placeholder="e.g., Best Employee Award, Research Paper Title, Volunteer Position",
                lines=2,
                interactive=True
            )
            item_organization = gr.Textbox(
                label="Organization/Publisher", 
                placeholder="e.g., Company Name, Journal Name, Non-profit Organization",
                lines=2,
                interactive=True
            )
            
        with gr.Row():
            item_date = gr.Textbox(
                label="Date", 
                placeholder="e.g., 2023, March 2023, 2022-2023",
                lines=2,
                interactive=True
            )
            item_location = gr.Textbox(
                label="Location (Optional)", 
                placeholder="e.g., New York, Online, Remote",
                lines=2,
                interactive=True
            )
            
        with gr.Row():
            item_description = gr.Textbox(
                label="Description (Optional)", 
                placeholder="Brief description of the achievement, publication, activity, or responsibility",
                lines=3,
                interactive=True
            )
            
        with gr.Row():
            item_url = gr.Textbox(
                label="URL/Link (Optional)", 
                placeholder="https://... (e.g., publication link, organization website)",
                lines=2,
                interactive=True
            )
            
        with gr.Row():
            add_item_btn = gr.Button("➕ Add Item", variant="primary")
            reset_form_btn = gr.Button("🔄 Reset Form")
        gr.Markdown("---\n### 📋 Your Additional Sections")
        
        sections_display = gr.Dataframe(
            headers=["Section", "Title", "Organization", "Date", "Location", "Description", "URL"],
            datatype=["str", "str", "str", "str", "str", "str", "str"],
            type="array",
            col_count=(7, "fixed"),
            row_count=15,
            interactive=True,
            value=[],
            label="Additional Resume Sections & Items",
            wrap=True,
            column_widths=["10%", "25%", "15%", "8%", "12%", "20%", "10%"]
        )

        with gr.Row():
            move_up_btn = gr.Button("⬆️ Move Up")
            move_down_btn = gr.Button("⬇️ Move Down")
            remove_item_btn = gr.Button("🗑️ Remove Item", variant="secondary")
            clear_all_btn = gr.Button("💥 Clear All", variant="secondary")
        selected_idx = gr.State(None)
        sections_data = gr.State({})
        def toggle_custom_section_input(selected_section):
            if selected_section == "➕ Create New Section...":
                return gr.update(visible=True)
            else:
                return gr.update(visible=False)
        
        section_selector.change(
            toggle_custom_section_input,
            [section_selector],
            [custom_section_row]
        )
        def create_section(section_name, current_sections):
            if not section_name or not section_name.strip():
                return current_sections, gr.update(), gr.update(visible=False), "⚠️ Please enter a section name"
                
            section_name = section_name.strip()
            if section_name in current_sections:
                return current_sections, gr.update(), gr.update(visible=False), f"⚠️ Section '{section_name}' already exists"
            new_sections = current_sections.copy()
            new_sections[section_name] = []
            predefined_sections = [s for s in COMMON_SECTIONS if s != "➕ Create New Section..."]
            # Filter out custom sections that already exist in predefined to avoid duplicates
            custom_sections = [s for s in new_sections.keys() if s not in predefined_sections]
            all_sections = predefined_sections + custom_sections + ["➕ Create New Section..."]
            
            return (
                new_sections, 
                gr.update(choices=all_sections, value=section_name), 
                gr.update(visible=False),
                f"✅ Created section '{section_name}'"
            )

        create_section_btn.click(
            create_section,
            [custom_section_input, sections_data],
            [sections_data, section_selector, custom_section_row, gr.Textbox(visible=False)]
        )
        def reset_form():
            return [""] * 6
            
        reset_form_btn.click(
            reset_form,
            None,
            [item_title, item_organization, item_date, item_location, item_description, item_url]
        )
        def add_item_to_section(selected_section, title, org, date, location, desc, url, current_sections, current_table):
            if not selected_section or selected_section == "➕ Create New Section...":
                return current_sections, current_table, "⚠️ Please select a section first (create a new section if needed)"
                
            if not title or not title.strip():
                return current_sections, current_table, "⚠️ Please enter a title"
            new_item = {
                "title": title.strip(),
                "organization": org.strip() if org else "",
                "date": date.strip() if date else "",
                "location": location.strip() if location else "",
                "description": desc.strip() if desc else "",
                "url": url.strip() if url else ""
            }
            updated_sections = current_sections.copy()
            if selected_section not in updated_sections:
                updated_sections[selected_section] = []
            updated_sections[selected_section].append(new_item)
            new_table = generate_table_from_sections(updated_sections)
            
            return updated_sections, new_table, f"✅ Added '{title}' to {selected_section}"

        add_item_btn.click(
            add_item_to_section,
            [section_selector, item_title, item_organization, item_date, item_location, item_description, item_url, sections_data, sections_display],
            [sections_data, sections_display, gr.Textbox(visible=False)]
        )
        def capture_row(evt: gr.SelectData):
            idx = evt.index
            if idx is None:
                return None
            return idx[0] if isinstance(idx, (list, tuple)) else int(idx)

        sections_display.select(capture_row, None, selected_idx)
        def remove_item(table_data, idx, current_sections):
            if idx is None or not (0 <= idx < len(table_data)):
                return current_sections, table_data, None
                
            new_table = [list(row) for row in table_data]
            removed_row = new_table.pop(idx)
            section_name = removed_row[0]
            item_title = removed_row[1]
            
            updated_sections = current_sections.copy()
            if section_name in updated_sections:
                updated_sections[section_name] = [
                    item for item in updated_sections[section_name] 
                    if item["title"] != item_title
                ]
            
            return updated_sections, new_table, None

        remove_item_btn.click(
            remove_item,
            [sections_display, selected_idx, sections_data],
            [sections_data, sections_display, selected_idx]
        )
        def move_up(table_data, idx, current_sections):
            if idx is None or idx <= 0 or idx >= len(table_data):
                return current_sections, table_data, idx
            
            new_table = [list(row) for row in table_data]
            new_table[idx - 1], new_table[idx] = new_table[idx], new_table[idx - 1]
            
            updated_sections = {}
            for row in new_table:
                section_name = row[0]
                if section_name not in updated_sections:
                    updated_sections[section_name] = []
                    
                item = {
                    "title": row[1],
                    "organization": row[2],
                    "date": row[3],
                    "location": row[4],
                    "description": row[5],
                    "url": row[6]
                }
                updated_sections[section_name].append(item)
            
            return updated_sections, new_table, idx - 1

        move_up_btn.click(
            move_up,
            [sections_display, selected_idx, sections_data],
            [sections_data, sections_display, selected_idx]
        )

        def move_down(table_data, idx, current_sections):
            if idx is None or idx < 0 or idx >= len(table_data) - 1:
                return current_sections, table_data, idx
            
            new_table = [list(row) for row in table_data]
            new_table[idx + 1], new_table[idx] = new_table[idx], new_table[idx + 1]
            
            updated_sections = {}
            for row in new_table:
                section_name = row[0]
                if section_name not in updated_sections:
                    updated_sections[section_name] = []
                    
                item = {
                    "title": row[1],
                    "organization": row[2],
                    "date": row[3],
                    "location": row[4],
                    "description": row[5],
                    "url": row[6]
                }
                updated_sections[section_name].append(item)
            
            return updated_sections, new_table, idx + 1

        move_down_btn.click(
            move_down,
            [sections_display, selected_idx, sections_data],
            [sections_data, sections_display, selected_idx]
        )
        def clear_all():
            predefined_sections = [s for s in COMMON_SECTIONS if s != "➕ Create New Section..."]
            return {}, [], gr.update(choices=COMMON_SECTIONS, value=predefined_sections[0] if predefined_sections else None), None

        clear_all_btn.click(
            clear_all,
            None,
            [sections_data, sections_display, section_selector, selected_idx]
        )
        def load_data_from_dict(others_dict):
            """Load Others data from a dictionary (e.g., from JSON import)"""
            predefined_sections = [s for s in COMMON_SECTIONS if s != "➕ Create New Section..."]
            
            if not others_dict or not isinstance(others_dict, dict):
                return {}, [], gr.update(choices=COMMON_SECTIONS, value=predefined_sections[0] if predefined_sections else None), None
            table_data = generate_table_from_sections(others_dict)
            # Filter out custom sections that already exist in predefined to avoid duplicates
            custom_sections = [s for s in others_dict.keys() if s not in predefined_sections]
            all_sections = predefined_sections + custom_sections + ["➕ Create New Section..."]
            selected = list(others_dict.keys())[0] if others_dict else (predefined_sections[0] if predefined_sections else None)
            
            return others_dict, table_data, gr.update(choices=all_sections, value=selected), None
    components = {
        "section_selector": section_selector,
        "item_title": item_title,
        "item_organization": item_organization,
        "item_date": item_date,
        "item_location": item_location,
        "item_description": item_description,
        "item_url": item_url,
        "sections_display": sections_display,
        "sections_data": sections_data,
        "selected_idx": selected_idx,
        "load_data_from_dict": load_data_from_dict
    }
    
    return SimpleNamespace(tab=tab, components=components) 