# -*- coding: utf-8 -*-
import logging
from odoo import models

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    def _spt_is_step_transfer(self):
        self.ensure_one()
        return self.picking_type_id.code in ('incoming', 'internal')

    def _spt_has_partial_selection(self):
        """Return True only when SOME (not zero, not all) moves are selected."""
        self.ensure_one()
        moves = self.move_ids.filtered(lambda m: m.state not in ('done', 'cancel'))
        if not moves:
            return False
        selected = moves.filtered('is_selected_for_transfer')
        # None selected → treat as all selected (normal flow)
        if not selected:
            return False
        # All selected → normal flow
        if len(selected) == len(moves):
            return False
        # Partial → custom flow
        return True

    # ------------------------------------------------------------------
    # Core override
    # ------------------------------------------------------------------

    def button_validate(self):
        if len(self) > 1:
            result = None
            for picking in self:
                res = picking.button_validate()
                if isinstance(res, dict) and res.get('type') == 'ir.actions.act_window':
                    result = res
            return result or True

        self.ensure_one()

        # Gate: only intercept step-transfers with a partial selection
        if not self._spt_is_step_transfer() or not self._spt_has_partial_selection():
            return super().button_validate()

        _logger.debug(
            "stock_partial_transfer: partial move selection on picking %s", self.name
        )

        # Un-selected moves → zero out qty_done on all their detail lines
        # so Odoo's backorder wizard handles them naturally.
        unselected_moves = self.move_ids.filtered(
            lambda m: not m.is_selected_for_transfer
                      and m.state not in ('done', 'cancel')
        )

        # Save original done quantities per move line for rollback on error
        original_qty = {
            line.id: line.qty_done
            for move in unselected_moves
            for line in move.move_line_ids
        }

        for move in unselected_moves:
            move.move_line_ids.write({'qty_done': 0.0})

        try:
            result = super().button_validate()
        except Exception:
            # Rollback to avoid corrupted state
            for move in unselected_moves:
                for line in move.move_line_ids:
                    line.qty_done = original_qty.get(line.id, 0.0)
            raise

        # Reset flags on any backorder lines so the next operator starts fresh
        if self.exists() and self.state not in ('done', 'cancel'):
            self.move_ids.write({'is_selected_for_transfer': False})

        return result
