from odoo import _, api, fields, models
from odoo.exceptions import UserError

class ComplaintStage(models.Model):
    _name = 'complaint.stage'
    _order = 'sequence, id'

    sequence = fields.Integer(default=50)
    name = fields.Char()
    fold = fields.Boolean()

class ComplaintComplaint(models.Model):
    _name = 'complaint.complaint'

    @api.model
    def _get_default_name(self):
        # Set the name from sequence.
        return self.env['ir.sequence'].next_by_code('complaint.complaint')
    
    @api.model
    def _get_default_stage_id(self):
        # Since stages are order by sequence first, this should fetch the one with the lowest sequence number.
        return self.env['complaint.stage'].search([], limit=1)
    
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        # If it's opened from the 'All' menu, then return all stages.
        # But if it's opened from 'Need Supervision' menu, return only 'In Progress' stage.
        if domain:
            domain = [('name','=','In Progress')]
        return self.env['complaint.stage'].search(domain, order=order)

    name = fields.Char('Complaint Number', copy=False, default=_get_default_name)
    tenant_name = fields.Char()
    email = fields.Char()
    address = fields.Text()
    problem_type = fields.Selection([
        ('question','Question'),
        ('electrical','Electrical Issue'),
        ('heating','Heating Issue'),
        ('other','Other'),
    ])
    description = fields.Text()
    stage_id = fields.Many2one('complaint.stage', copy=False, default=_get_default_stage_id, group_expand='_read_group_stage_ids')
    stage_name = fields.Char(related='stage_id.name')
    action_plan = fields.Text(help='This can be a message if the problem type is a question. Otherwise, this is the action plan.')
    message_has_sent = fields.Boolean()
    work_order_has_printed = fields.Boolean()

    def set_in_review(self):
        # Set the stage to 'In Review' from the form view.
        self.stage_id = self.env['complaint.stage'].search([('name','=','In Review')], limit=1).id

    def set_in_progress(self):
        # Set the stage to 'In Progress' from the form view.
        self.stage_id = self.env['complaint.stage'].search([('name','=','In Progress')], limit=1).id

    def set_dropped(self):
        # Drop from the form view.
        self.stage_id = self.env['complaint.stage'].search([('name','=','Dropped')], limit=1).id

    def send_message(self):
        # The email should contain the answer for the question.
        if not self.action_plan:
            raise UserError(_("Please provide the message first."))
        mail_vals = {
            'email_from': self.env.company.email,
            'subject': 'The answer for your question.',
            'email_to': self.email,
            #TODO : create a more intentional template.
            'body_html': self.action_plan
        }
        mail = self.env['mail.mail'].sudo().with_context(
            mail_create_nosubscribe=True,
        ).create(mail_vals)
        mail.send()
        # Set the stage to 'Solved' and set the flag that the message has been sent.
        self.write({
            'stage_id': self.env['complaint.stage'].search([('name','=','Solved')], limit=1).id,
            'message_has_sent': True
        })

    def print_work_order(self):
        # Set the stage to 'Solved' and set the flag that the work order has been printed.
        self.write({
            'stage_id': self.env['complaint.stage'].search([('name','=','Solved')], limit=1).id,
            'work_order_has_printed': True
        })
        return self.env.ref('real_estate_x_complaint.action_report_work_order').report_action(self)

    @api.model
    def create(self, vals):
        res = super(ComplaintComplaint, self).create(vals)
        # Send an email to tell the tenant that their complaint has been sent to us.
        mail_vals = {
            'email_from': self.env.company.email,
            'subject': 'Your complaint was sent.',
            'email_to': res.email,
            #TODO : create a more intentional template
            'body_html': 'Your complaint with number %s was successfully sent.'%res.name
        }
        mail = self.env['mail.mail'].sudo().with_context(
            mail_create_nosubscribe=True,
        ).create(mail_vals)
        mail.send()
        return res
    
    def write(self, vals):
        # Check all constraints when updating stage, expecially when updating by dragging from kanban view
        if 'stage_id' in vals:
            stages = self.env['complaint.stage'].search([])
            stages_dict = {
                stage.id : stage.name for stage in stages
            }
            match stages_dict[vals['stage_id']]:
                case 'In Progress':
                    if self.problem_type == 'question':
                        raise UserError(_("You can directly close a 'question' complaint by sending the answer message."))
                    elif not self.action_plan:
                        raise UserError(_("Please provide the action plan first."))
                case 'Solved':
                    if self.problem_type == 'question' and not self.message_has_sent and 'message_has_sent' not in vals:
                        raise UserError(_("Please send the answer message for the question first."))
                    elif self.problem_type != 'question' and not self.work_order_has_printed and 'work_order_has_printed' not in vals:
                        raise UserError(_("You need to print the work order first."))
                    elif not self.action_plan:
                        raise UserError(_("You can't solve the complaint without action plan."))
                    # Send an email informing tenant that the complaint has been solved.
                    mail_vals = {
                        'email_from': self.env.company.email,
                        'subject': 'Your complaint is solved!',
                        'email_to': self.email,
                        #TODO : create a more intentional template
                        'body_html': 'Your complaint with number %s is successfully solved.'%self.name
                    }
                    mail = self.env['mail.mail'].sudo().with_context(
                        mail_create_nosubscribe=True,
                    ).create(mail_vals)
                    mail.send()
                case 'Dropped':
                    if self.stage_name == 'Solved':
                        raise UserError(_('The complaint is already solved.'))
                    # Send an email informing tenant that the complaint is dropped. doc.
                    mail_vals = {
                        'email_from': self.env.company.email,
                        'subject': 'Your complaint is dropped!',
                        'email_to': self.email,
                        #TODO : create a more intentional template
                        'body_html': 'Your complaint with number %s is dropped because of some reasons.'%self.name
                    }
                    mail = self.env['mail.mail'].sudo().with_context(
                        mail_create_nosubscribe=True,
                    ).create(mail_vals)
                    mail.send()

        return super(ComplaintComplaint, self).write(vals)