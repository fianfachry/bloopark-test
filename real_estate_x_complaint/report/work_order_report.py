from odoo import models,api

# Needed for printing the workorder.
class WorkOrderReport(models.AbstractModel):
    _name = 'report.real_estate_x_complaint.report_work_order'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['complaint.complaint'].browse(docids)
        return {
            'doc': docs,
        }