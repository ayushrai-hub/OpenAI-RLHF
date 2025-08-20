
def print_active_tab_content(self):
    """Print the active tab's name, index, and its variables."""
    current_index = self.ui.alias_tab_widget_editor_page.currentIndex()
    if current_index == -1:
        print("No active tab.")
        return

    # Get tab information
    tab_name = self.ui.alias_tab_widget_editor_page.tabText(current_index)
    print(f"\nActive Tab - Index: {current_index}, Name: {tab_name}")

    # Get table widget from active tab
    table_widget = self.get_table_widget_from_tab(current_index)
    if not table_widget:
        print("No table widget found in the active tab.")
        return

    # Print all variables in the table
    print("\nVariables in this tab:")
    print("-" * 50)
    print(f"{'Variable Name':<30} {'Value':<30} {'Type':<15}")
    print("-" * 50)

    for row in range(table_widget.rowCount()):
        # Get variable name
        name_item = table_widget.item(row, 0)
        name = name_item.text() if name_item else ""

        # Get variable value
        value_item = table_widget.item(row, 1)
        value = value_item.text() if value_item else ""

        # Get variable type from combo box
        type_widget = table_widget.cellWidget(row, 2)
        var_type = type_widget.currentText() if type_widget else "None"

        print(f"{name:<30} {value:<30} {var_type:<15}")
    
    print("-" * 50)


def print_active_tab_content_detailed(self):
    """Print detailed information about the active tab and its variables."""
    current_index = self.ui.alias_tab_widget_editor_page.currentIndex()
    if current_index == -1:
        print("No active tab.")
        return

    # Tab Information
    tab_name = self.ui.alias_tab_widget_editor_page.tabText(current_index)
    print("\n=== Tab Information ===")
    print(f"Index: {current_index}")
    print(f"Name: {tab_name}")

    # Get table widget
    table_widget = self.get_table_widget_from_tab(current_index)
    if not table_widget:
        print("No table widget found in the active tab.")
        return

    # Variables Information
    print("\n=== Variables ===")
    for row in range(table_widget.rowCount()):
        print(f"\nVariable #{row + 1}:")
        print("-" * 20)
        
        # Name
        name_item = table_widget.item(row, 0)
        name = name_item.text() if name_item else "N/A"
        print(f"Name: {name}")
        
        # Value
        value_item = table_widget.item(row, 1)
        value = value_item.text() if value_item else "N/A"
        print(f"Value: {value}")
        
        # Type
        type_widget = table_widget.cellWidget(row, 2)
        var_type = type_widget.currentText() if type_widget else "None"
        print(f"Type: {var_type}")

    print("\n=== End of Tab Content ===")
