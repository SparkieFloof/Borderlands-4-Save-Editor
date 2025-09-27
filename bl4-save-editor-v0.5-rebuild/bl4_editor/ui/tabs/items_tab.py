# Updated bl4_editor/ui/tabs/items_tab.py  
from PySide6 import QtWidgets, QtCore
from typing import Any, Dict, List
from bl4_editor.core import logger

class ItemsTab(QtWidgets.QWidget):
    """Items tab with subtabs for different item categories"""
    
    def __init__(self):
        super().__init__()
        self.data = {}
        # keep original raw item dicts for precise round-tripping
        self._original_items = {}
        self.backpack_rows = []
        self.equipped_rows = []
        self.bank_rows = []
        self.unknown_rows = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup items tab UI with subtabs"""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Sub-tabs for different item types
        self.subtabs = QtWidgets.QTabWidget()
        layout.addWidget(self.subtabs)
        
        # Create tables for each item type
        self.backpack_table = self._create_items_table()
        self.equipped_table = self._create_items_table()
        self.bank_table = self._create_items_table()
        self.unknown_table = self._create_items_table()
        
        # Add tables to subtabs (initially hidden)
        self.subtabs.addTab(self.backpack_table, "Backpack")
        self.subtabs.addTab(self.equipped_table, "Equipped") 
        self.subtabs.addTab(self.bank_table, "Bank")
        self.subtabs.addTab(self.unknown_table, "Unknown")
        
        # Buttons for item management
        button_layout = QtWidgets.QHBoxLayout()
        self.btn_add_item = QtWidgets.QPushButton("Add Item")
        self.btn_remove_item = QtWidgets.QPushButton("Remove Selected")
        self.btn_duplicate_item = QtWidgets.QPushButton("Duplicate Selected")
        
        button_layout.addWidget(self.btn_add_item)
        button_layout.addWidget(self.btn_remove_item)
        button_layout.addWidget(self.btn_duplicate_item)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Connect buttons
        self.btn_add_item.clicked.connect(self._add_item_to_current_table)
        self.btn_remove_item.clicked.connect(self._remove_selected_item)
        self.btn_duplicate_item.clicked.connect(self._duplicate_selected_item)
    
    def _create_items_table(self) -> QtWidgets.QTableWidget:
        """Create a table widget for items"""
        table = QtWidgets.QTableWidget(0, 4)
        table.setHorizontalHeaderLabels(["Slot", "Serial", "Flags", "Notes"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked | 
                             QtWidgets.QAbstractItemView.SelectedClicked)
        return table
    
    def load_data(self, data: Dict[str, Any]):
        """Load items data from save file"""
        # Clear any previously loaded data first to avoid leaking state between files
        self.data = {}
        self._original_items.clear()
        # clear UI tables immediately
        try:
            self.backpack_table.setRowCount(0)
            self.equipped_table.setRowCount(0)
            self.bank_table.setRowCount(0)
            self.unknown_table.setRowCount(0)
        except Exception:
            pass

        # reset row lists
        self.backpack_rows = []
        self.equipped_rows = []
        self.bank_rows = []
        self.unknown_rows = []

        # now assign incoming data and populate
        self.data = data if data else {}
        logger.debug('ItemsTab: load_data called')
        self._populate_items_from_data()
    
    def _populate_items_from_data(self):
        """Extract items from data structure and populate tables"""
        # ensure originals and row lists are fresh
        if not isinstance(self._original_items, dict):
            self._original_items = {}
        else:
            # keep existing dict object but clear contents
            self._original_items.clear()

        self.backpack_rows = []
        self.equipped_rows = []
        self.bank_rows = []
        self.unknown_rows = []

        # clear table rows before repopulating
        try:
            self.backpack_table.setRowCount(0)
            self.equipped_table.setRowCount(0)
            self.bank_table.setRowCount(0)
            self.unknown_table.setRowCount(0)
        except Exception:
            pass
        
        # Check for profile-style data first (shared.inventory or domains.local.shared.inventory)
        profile_inventory = None
        try:
            if 'shared' in self.data and isinstance(self.data['shared'], dict):
                profile_inventory = self.data['shared'].get('inventory', None)
        except Exception:
            profile_inventory = None

        # check nested domains.local.shared.inventory path used by some exports
        if profile_inventory is None and 'domains' in self.data and isinstance(self.data['domains'], dict):
            try:
                local = self.data['domains'].get('local', {})
                if isinstance(local, dict) and 'shared' in local and isinstance(local['shared'], dict):
                    profile_inventory = local['shared'].get('inventory', None)
            except Exception:
                profile_inventory = None

        if isinstance(profile_inventory, dict):
            items = profile_inventory.get('items', {})
            if isinstance(items, dict):
                bank = items.get('bank', {})
                if isinstance(bank, dict):
                    for slot, item_data in bank.items():
                        if isinstance(item_data, dict):
                            # store original for preservation
                            self._original_items[slot] = item_data
                            self.bank_rows.append({
                                'slot': slot,
                                'serial': item_data.get('serial', ''),
                                'flags': item_data.get('state_flags', 0),
                                'notes': item_data.get('notes', '')
                            })
        else:
            # Character save data
            # primary inventory path
            inventory = self.data.get('inventory', {})
            if isinstance(inventory, dict):
                items = inventory.get('items', {})
                if isinstance(items, dict):
                    # Backpack items
                    backpack = items.get('backpack', {})
                    if isinstance(backpack, dict):
                        for slot, item_data in backpack.items():
                            if isinstance(item_data, dict):
                                self._original_items[slot] = item_data
                                self.backpack_rows.append({
                                    'slot': slot,
                                    'serial': item_data.get('serial', ''),
                                    'flags': item_data.get('state_flags', 0),
                                    'notes': item_data.get('notes', '')
                                })
                    
                    # Unknown items
                    unknown = items.get('unknown_items', [])
                    if isinstance(unknown, list):
                        for idx, item_data in enumerate(unknown):
                            if isinstance(item_data, dict):
                                key = f'unknown_{idx}'
                                self._original_items[key] = item_data
                                self.unknown_rows.append({
                                    'slot': key,
                                    'serial': item_data.get('serial', ''),
                                    'flags': item_data.get('state_flags', 0),
                                    'notes': item_data.get('notes', '')
                                })
            
            # Equipped items: try multiple places and support various layouts
            equipped_found = False

            def _process_equipped_container(container) -> bool:
                """Process a container that may hold equipped items in several formats.
                Returns True if any items were added."""
                added = False
                if isinstance(container, dict):
                    # container might map slot -> list or slot -> dict
                    for slot, val in container.items():
                        if isinstance(val, list):
                            for idx, item_data in enumerate(val):
                                if isinstance(item_data, dict):
                                    key = f'{slot}_{idx}'
                                    self._original_items[key] = item_data
                                    self.equipped_rows.append({
                                        'slot': key,
                                        'serial': item_data.get('serial', ''),
                                        'flags': item_data.get('state_flags', 0),
                                        'notes': item_data.get('notes', '')
                                    })
                                    added = True
                        elif isinstance(val, dict):
                            # single item directly stored under slot
                            item_data = val
                            key = f'{slot}_0'
                            self._original_items[key] = item_data
                            self.equipped_rows.append({
                                'slot': key,
                                'serial': item_data.get('serial', ''),
                                'flags': item_data.get('state_flags', 0),
                                'notes': item_data.get('notes', '')
                            })
                            added = True
                elif isinstance(container, list):
                    for idx, item_data in enumerate(container):
                        if isinstance(item_data, dict):
                            key = f'item_{idx}'
                            self._original_items[key] = item_data
                            self.equipped_rows.append({
                                'slot': key,
                                'serial': item_data.get('serial', ''),
                                'flags': item_data.get('state_flags', 0),
                                'notes': item_data.get('notes', '')
                            })
                            added = True
                return added

            # 1) state.inventory.equipped_inventory or similar
            try:
                state = self.data.get('state', {})
                if isinstance(state, dict):
                    inv = state.get('inventory', {})
                    if isinstance(inv, dict):
                        equipped_inv = inv.get('equipped_inventory') or inv.get('equippedInventory') or inv.get('equipped')
                        if equipped_inv is not None:
                            if _process_equipped_container(equipped_inv):
                                equipped_found = True
            except Exception:
                equipped_found = False

            # 2) fallback to top-level equipped_inventory (older layout)
            if not equipped_found:
                equipped_inv = self.data.get('equipped_inventory') or self.data.get('equippedInventory') or self.data.get('equipped')
                if equipped_inv is not None:
                    if _process_equipped_container(equipped_inv):
                        equipped_found = True

            # 3) lostloot handling (state.lostloot.items)
            try:
                lost = None
                state = self.data.get('state', {})
                if isinstance(state, dict):
                    lostloot = state.get('lostloot', {})
                    if isinstance(lostloot, dict):
                        lost = lostloot.get('items', None)
                if lost and isinstance(lost, dict):
                    for slot, item_data in lost.items():
                        if isinstance(item_data, dict):
                            key = f'lost_{slot}'
                            self._original_items[key] = item_data
                            self.unknown_rows.append({
                                'slot': key,
                                'serial': item_data.get('serial', ''),
                                'flags': item_data.get('state_flags', 0),
                                'notes': item_data.get('notes', '')
                            })
            except Exception:
                pass
        
        # Populate tables
        self._populate_table(self.backpack_table, self.backpack_rows)
        self._populate_table(self.equipped_table, self.equipped_rows)
        self._populate_table(self.bank_table, self.bank_rows)
        self._populate_table(self.unknown_table, self.unknown_rows)
        
        # Show/hide tabs based on data
        self._adjust_subtab_visibility()
    
    def _populate_table(self, table: QtWidgets.QTableWidget, rows: List[Dict]):
        """Populate a table with item rows"""
        table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(row_data.get('slot', '')))
            table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(str(row_data.get('serial', ''))))
            table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(str(row_data.get('flags', 0))))
            table.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(row_data.get('notes', '')))
        
        # Make slot column read-only
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item:
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
    
    def _adjust_subtab_visibility(self):
        """Show/hide subtabs based on available data"""
        # Remove all tabs first
        while self.subtabs.count() > 0:
            self.subtabs.removeTab(0)
        
        # Add tabs that have data
        if self.backpack_rows:
            self.subtabs.addTab(self.backpack_table, f"Backpack ({len(self.backpack_rows)})")
        if self.equipped_rows:
            self.subtabs.addTab(self.equipped_table, f"Equipped ({len(self.equipped_rows)})")
        if self.bank_rows:
            self.subtabs.addTab(self.bank_table, f"Bank ({len(self.bank_rows)})")
        if self.unknown_rows:
            self.subtabs.addTab(self.unknown_table, f"Unknown ({len(self.unknown_rows)})")
        
        # Always show at least one tab
        if self.subtabs.count() == 0:
            self.subtabs.addTab(self.backpack_table, "Backpack")
        # log counts for debugging
        logger.info(f'ItemsTab loaded: backpack={len(self.backpack_rows)}, equipped={len(self.equipped_rows)}, bank={len(self.bank_rows)}, unknown={len(self.unknown_rows)}')
    
    def _add_item_to_current_table(self):
        """Add new item to currently active table"""
        current_table = self.subtabs.currentWidget()
        if isinstance(current_table, QtWidgets.QTableWidget):
            row = current_table.rowCount()
            current_table.insertRow(row)
            current_table.setItem(row, 0, QtWidgets.QTableWidgetItem(f"slot_{row}"))
            current_table.setItem(row, 1, QtWidgets.QTableWidgetItem("new_item_serial"))
            current_table.setItem(row, 2, QtWidgets.QTableWidgetItem("0"))
            current_table.setItem(row, 3, QtWidgets.QTableWidgetItem(""))
    
    def _remove_selected_item(self):
        """Remove selected item from current table"""
        current_table = self.subtabs.currentWidget()
        if isinstance(current_table, QtWidgets.QTableWidget):
            current_row = current_table.currentRow()
            if current_row >= 0:
                current_table.removeRow(current_row)
    
    def _duplicate_selected_item(self):
        """Duplicate selected item in current table"""
        current_table = self.subtabs.currentWidget()
        if isinstance(current_table, QtWidgets.QTableWidget):
            current_row = current_table.currentRow()
            if current_row >= 0:
                # Copy data from current row
                slot_item = current_table.item(current_row, 0)
                serial_item = current_table.item(current_row, 1) 
                flags_item = current_table.item(current_row, 2)
                notes_item = current_table.item(current_row, 3)
                
                # Insert new row
                new_row = current_table.rowCount()
                current_table.insertRow(new_row)
                
                # Copy data to new row
                current_table.setItem(new_row, 0, QtWidgets.QTableWidgetItem(f"slot_{new_row}"))
                current_table.setItem(new_row, 1, QtWidgets.QTableWidgetItem(serial_item.text() if serial_item else ""))
                current_table.setItem(new_row, 2, QtWidgets.QTableWidgetItem(flags_item.text() if flags_item else "0"))
                current_table.setItem(new_row, 3, QtWidgets.QTableWidgetItem(notes_item.text() if notes_item else ""))
    
    def save_data(self) -> Dict[str, Any]:
        """Collect data from tables back into save structure"""
        # Extract current table data
        backpack_data = self._extract_table_data(self.backpack_table)
        equipped_data = self._extract_table_data(self.equipped_table)
        bank_data = self._extract_table_data(self.bank_table) 
        unknown_data = self._extract_table_data(self.unknown_table)
        
    # Update data structure based on what type of save this is
        if 'shared' in self.data:
            # Profile save - update bank
            if not isinstance(self.data.get('shared'), dict):
                self.data['shared'] = {}
            if not isinstance(self.data['shared'].get('inventory'), dict):
                self.data['shared']['inventory'] = {}
            if not isinstance(self.data['shared']['inventory'].get('items'), dict):
                self.data['shared']['inventory']['items'] = {}
            
            # Update bank items
            bank_dict = {}
            for item in bank_data:
                slot = item.get('slot', f"slot_{len(bank_dict)}")
                # preserve original item dict if exists
                orig = self._original_items.get(slot, {})
                merged = dict(orig) if isinstance(orig, dict) else {}
                # only overwrite fields user can change; keep serial exactly
                merged['state_flags'] = int(item.get('flags', merged.get('state_flags', 0)))
                if item.get('notes'):
                    merged['notes'] = item.get('notes')
                bank_dict[slot] = merged
            self.data['shared']['inventory']['items']['bank'] = bank_dict
        else:
            # Character save - update all item types
            if 'inventory' not in self.data:
                self.data['inventory'] = {}
            if 'items' not in self.data['inventory']:
                self.data['inventory']['items'] = {}
            
            # Update backpack
            if backpack_data:
                backpack_dict = {}
                for item in backpack_data:
                    slot = item.get('slot', f"slot_{len(backpack_dict)}")
                    orig = self._original_items.get(slot, {})
                    merged = dict(orig) if isinstance(orig, dict) else {}
                    merged['state_flags'] = int(item.get('flags', merged.get('state_flags', 0)))
                    if item.get('notes'):
                        merged['notes'] = item.get('notes')
                    # ensure serial preserved
                    if 'serial' not in merged and item.get('serial'):
                        merged['serial'] = item.get('serial')
                    backpack_dict[slot] = merged
                self.data['inventory']['items']['backpack'] = backpack_dict
            
            # Update unknown items
            if unknown_data:
                unknown_list = []
                for item in unknown_data:
                    key = item.get('slot')
                    orig = self._original_items.get(key, {})
                    merged = dict(orig) if isinstance(orig, dict) else {}
                    merged['state_flags'] = int(item.get('flags', merged.get('state_flags', 0)))
                    if item.get('notes'):
                        merged['notes'] = item.get('notes')
                    if 'serial' not in merged and item.get('serial'):
                        merged['serial'] = item.get('serial')
                    unknown_list.append(merged)
                self.data['inventory']['items']['unknown_items'] = unknown_list
            
            # Update equipped items
            if equipped_data:
                equipped_dict = {}
                for item in equipped_data:
                    slot_token = item.get('slot', 'weapon_0')
                    parts = slot_token.split('_')
                    # reconstruct base key like 'slot_5' from first two parts when present
                    if len(parts) >= 2 and parts[1].isdigit():
                        base_key = f"{parts[0]}_{parts[1]}"
                        index = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
                    else:
                        base_key = parts[0]
                        index = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0

                    if base_key not in equipped_dict:
                        equipped_dict[base_key] = []

                    # Build merged item preserving serial
                    key = f"{base_key}_{index}"
                    orig = self._original_items.get(key, {})
                    merged = dict(orig) if isinstance(orig, dict) else {}
                    merged['state_flags'] = int(item.get('flags', merged.get('state_flags', 0)))
                    if item.get('notes'):
                        merged['notes'] = item.get('notes')
                    if 'serial' not in merged and item.get('serial'):
                        merged['serial'] = item.get('serial')

                    # Append to list at the correct index position
                    lst = equipped_dict[base_key]
                    # ensure list large enough
                    while len(lst) <= index:
                        lst.append({})
                    lst[index] = merged

                if 'equipped_inventory' not in self.data:
                    self.data['equipped_inventory'] = {}
                self.data['equipped_inventory']['equipped'] = equipped_dict
        
        return self.data
    
    def _extract_table_data(self, table: QtWidgets.QTableWidget) -> List[Dict]:
        """Extract data from a table widget"""
        data = []
        for row in range(table.rowCount()):
            item_data = {}
            slot_item = table.item(row, 0)
            serial_item = table.item(row, 1)
            flags_item = table.item(row, 2)
            notes_item = table.item(row, 3)
            
            if slot_item:
                item_data['slot'] = slot_item.text()
            if serial_item:
                item_data['serial'] = serial_item.text()
            if flags_item:
                try:
                    item_data['flags'] = int(flags_item.text())
                except ValueError:
                    item_data['flags'] = 0
            if notes_item:
                item_data['notes'] = notes_item.text()
            
            data.append(item_data)
        return data

