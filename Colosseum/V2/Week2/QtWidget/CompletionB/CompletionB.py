

def print_active_tab_with_variables(self):
    """Print the name, index, and variables of the current active tab."""
    current_index = self.ui.alias_tab_widget_editor_page.currentIndex()
    if current_index != -1:
        tab_name = self.ui.alias_tab_widget_editor_page.tabText(current_index)
        print(f"Active Tab - Index: {current_index}, Name: {tab_name}")
        
        # Get the QTableWidget from the current tab
        table_widget = self.get_table_widget_from_tab(current_index)
        
        if table_widget:
            print("Variables in this tab:")
            for row in range(table_widget.rowCount()):
                var_name = table_widget.item(row, 0).text() if table_widget.item(row, 0) else "N/A"
                var_value = table_widget.item(row, 1).text() if table_widget.item(row, 1) else "N/A"
                var_type = table_widget.cellWidget(row, 2).currentText() if table_widget.cellWidget(row, 2) else "N/A"
                print(f"  {var_name} = {var_value} (Type: {var_type})")
        else:
            print("No table widget found in this tab.")
    else:
        print("No active tab.")

def get_table_widget_from_tab(self, index: int) -> QTableWidget:
    """Retrieve the QTableWidget from the given tab index."""
    tab_widget = self.ui.alias_tab_widget_editor_page.widget(index)
    if tab_widget:
        layout = tab_widget.layout()
        if layout and layout.count() > 0:
            table_widget = layout.itemAt(0).widget()
            if isinstance(table_widget, QTableWidget):
                return table_widget
    return None
