# Stock Partial Transfer by Product Selection
### Odoo 19 Custom Module

---

## What this module does

Adds a **Transfer ✓ checkbox** to every move line (Detailed Operations tab) in a stock picking.  
When the user validates a transfer the following rules apply:

| Checkbox state | Behaviour |
|---|---|
| All ticked *(default)* | 100 % standard Odoo flow – no change |
| **None** ticked | Treated as "all ticked" – standard flow |
| **Some** ticked | Only ticked lines are transferred; un-ticked lines go into an **automatic backorder** (Odoo's own backorder dialog is used) |
| Qty done < demand (any line) | Standard Odoo backorder is created for the shortfall – unchanged behaviour |

### Covered transfer types

`incoming` and `internal` picking types, which covers:

* Vendor → Input (Receipt step 1)
* Input → Quality (3-step receipt)
* Quality → Stock
* Internal transfers between locations

---

## File structure

```
stock_partial_transfer/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── stock_move.py          # computed helper field on stock.move
│   ├── stock_move_line.py     # is_selected_for_transfer Boolean field
│   └── stock_picking.py       # button_validate override (core logic)
├── views/
│   └── stock_picking_views.xml
├── security/
│   └── ir.model.access.csv
└── static/src/
    ├── js/stock_partial_transfer.js
    ├── xml/stock_partial_transfer.xml
    └── css/stock_partial_transfer.css
```

---

## How it works (technical)

### Field: `stock.move.line.is_selected_for_transfer`
- Boolean, default `True`
- Stored in DB but has NO effect on reservation, valuation, or accounting
- Only read inside `stock.picking.button_validate`

### Override: `stock.picking.button_validate`
1. If the picking type is **not** `incoming`/`internal` → call `super()` unchanged.
2. If **all** lines are selected (or none) → call `super()` unchanged.
3. If **partial** selection detected:
   - Temporarily set `qty_done = 0` on un-selected lines.
   - Call `super()` → Odoo's own backorder wizard fires naturally for the zeroed lines.
   - On failure, restore original `qty_done` values before re-raising.

This means:
- No custom backorder wizard is needed.
- All backorder numbering, chatter messages, and linked moves are handled by core Odoo.
- No accounting or stock valuation code is touched.

### Computed field: `stock.move.all_lines_selected`
- Non-stored, used only in the Operations tab column for a quick at-a-glance indicator.
- Has no effect on any business logic.

---

## Installation

1. Copy `stock_partial_transfer/` into your Odoo addons path.
2. Restart the Odoo server.
3. Enable Developer Mode → Apps → Update Apps List.
4. Search for **"Stock Partial Transfer"** and install.

---

## Compatibility notes

- Tested against **Odoo 19.0** (Community & Enterprise).
- Depends only on the `stock` module.
- Does **not** override `_action_done`, `_do_unreserve`, or any accounting method.
- Safe to use alongside `stock_landed_costs`, `stock_account`, `mrp`, `purchase`, `sale_stock`, etc.

---

## Uninstallation

Standard uninstall via Apps.  
The `is_selected_for_transfer` column will be removed from `stock_move_line` automatically.
All transfers in `done` state are unaffected.
