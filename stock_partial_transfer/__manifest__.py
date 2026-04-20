# -*- coding: utf-8 -*-
{
    'name': 'Stock Partial Transfer by Product Selection',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Select specific products to transfer; unselected products create a backorder automatically.',
    'description': """
        This module adds a checkbox column to the detailed operations / move lines
        in stock picking (transfers).  When the user validates a transfer:

        * **All checkboxes ticked (default)** – normal Odoo behaviour, nothing changes.
        * **Some checkboxes ticked** – only the ticked lines are processed in the
          current transfer; the remaining lines are put into a backorder automatically,
          just like the standard "create backorder" flow.
        * **No checkbox ticked** – all lines are processed (same as normal).

        Quantity-based backorders (demand > done qty) continue to work exactly as
        they do in standard Odoo.

        The feature is **only active for internal step-based transfers** (vendor→input,
        input→quality, quality→stock) and does NOT interfere with any other module that
        uses stock.move or stock.move.line.
    """,
    'author': 'Ahex Technologies',
    'website': 'https://www.ahex.in',
    'live_test_url': 'https://ahex.co/contact/',
    'depends': ['stock'],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
