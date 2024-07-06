from lxml import etree

from odoo import fields
from odoo.osv import expression
from odoo.tests import users
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

class TestComplaintCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestComplaintCommon, cls).setUpClass()

        # Test 'Question' Complaint
        cls.question_complaint = cls.env['complaint.complaint'].with_context({'mail_create_nolog': True}).create({
            'tenant_name': 'Fani',
            'email': 'fani@example.com',
            'address': 'Surabaya, Indonesia',
            'problem_type': 'question',
            'description': 'How to get access for the lift?',
        })

        # Test 'Electrical Issue' Complaint
        cls.electrical_complaint = cls.env['complaint.complaint'].with_context({'mail_create_nolog': True}).create({
            'tenant_name': 'Anggraini',
            'email': 'anggraini@example.com',
            'address': 'Surabaya, Indonesia',
            'problem_type': 'electrical',
            'description': 'I have power failure since last night!',
        })

        # Test 'Solved' Stage
        cls.solved_stage = cls.env['complaint.stage'].search([('name','=','Solved')], limit=1)

class TestComplaintBase(TestComplaintCommon):

    def test_default_name(self):
        name = self.question_complaint.name
        # Name automatically set according to the sequence.
        self.assertIsNotNone(name)

    def test_default_stage(self):
        Stages = self.env['complaint.stage']
        stage1 = Stages.create({
            'sequence': 1,
            'name': 'Stage 1'
        })
        Stages.create({
            'sequence': 2,
            'name': 'Stage 2'
        })
        complaint = self.env['complaint.complaint'].with_context({'mail_create_nolog': True}).create({
            'tenant_name': 'Tenant',
            'email': 'tenant@example.com',
            'address': 'Surabaya, Indonesia',
            'problem_type': 'question',
            'description': 'How to get access for the lift?',
        })
        # Stage automatically set to the lowest sequence while creation of the comlaint.
        self.assertEqual(stage1, complaint.stage_id)

    def test_write_stages(self):
        question_complaint = self.question_complaint
        electrical_complaint = self.electrical_complaint
        action_plan = 'Fix by engineer.'

        question_complaint.set_in_review()
        electrical_complaint.set_in_review()
        # The complaint stage is changed to 'In Review'.
        self.assertEqual(question_complaint.stage_name, 'In Review')

        # A question complaint can't be In Progress, instead directly set to Solved.
        with self.assertRaises(UserError):
            question_complaint.set_in_progress()

        # A complaint can't be In Progress when the action plan is not defined yet.
        with self.assertRaises(UserError):
            electrical_complaint.set_in_progress()

        electrical_complaint.write({
            'action_plan': action_plan
        })
        # Any field will be changed to the new value after writing.
        self.assertEqual(electrical_complaint.action_plan, action_plan)

        # A question complaint can't be moved to Solved through dragging in kanban view
        # Instead, use the 'Send Message' button in the form.
        with self.assertRaises(UserError):
            question_complaint.write({
                'stage_id': self.solved_stage.id
            })

        electrical_complaint.set_in_progress()
        # The complaint stage is changed to to 'In Progress'
        self.assertEqual(electrical_complaint.stage_name, 'In Progress')

        # A non question complaint can't be moved to Solved through dragging in kanban view
        # Instead, use the 'Drop' button in the form.
        with self.assertRaises(UserError):
            electrical_complaint.write({
                'stage_id': self.solved_stage.id
            })

        # A complaint can't be Solved when the action plan is not defined yet.
        with self.assertRaises(UserError):
            question_complaint.write({
                'stage_id': self.solved_stage.id,
                'message_has_sent': True
            })

        # A message can't be sent when the action plan is not defined yet.
        with self.assertRaises(UserError):
            question_complaint.send_message()

        question_complaint.write({
            'action_plan': 'Ask the receptionist.'
        })
        question_complaint.send_message()
        # After sending answer, the complaint's stage is set to Solved.
        self.assertEqual(question_complaint.stage_name, 'Solved')
        # After sending answer, the message_has_sent should be True.
        self.assertTrue(question_complaint.message_has_sent)

        electrical_complaint.print_work_order()
        # After printing work order, the complaint's stage is set to Solved.
        self.assertEqual(electrical_complaint.stage_name, 'Solved')
        # After printing work order, the work_order_has_printed should be True.
        self.assertTrue(electrical_complaint.work_order_has_printed)

        # Can't drop a Solved complaint.
        with self.assertRaises(UserError):
            question_complaint.set_dropped()

        complaint = self.env['complaint.complaint'].with_context({'mail_create_nolog': True}).create({
            'tenant_name': 'Tenant',
            'email': 'tenant@example.com',
            'address': 'Surabaya, Indonesia',
            'problem_type': 'question',
            'description': 'How to get access for the lift?',
        })
        complaint.set_dropped()
        # After dropping, the complaint's stage is set to Dropped.
        self.assertEqual(complaint.stage_name, 'Dropped')