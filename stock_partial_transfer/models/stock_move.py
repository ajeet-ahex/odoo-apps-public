from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    is_selected_for_transfer = fields.Boolean(
        string='Transfer',
        default=False,
        help=(
            "When checked, this move will be included in the current transfer.\n"
            "Un-check to exclude it; it will automatically be placed in a "
            "backorder instead.\n\n"
            "If no move is checked at all, all moves are transferred normally."
        ),
    )
