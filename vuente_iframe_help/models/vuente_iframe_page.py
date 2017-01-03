from openerp import api, models, fields, SUPERUSER_ID

class IrUiMenu(models.Model):

    _inherit = 'ir.ui.menu'

    iframe_pages_group = fields.Boolean(string="Parent menu for iframe pages")

    _defaults = {
        'parent_id': lambda self, cr, uid, ctx: ctx and ctx.get('default_iframe_pages_group') and self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vuente_iframe_help', 'menu_top')[1]
    }

class VuenteIframePage(models.Model):

    _name = 'vuente.iframe.page'
    _order = 'sequence'

    def get_default_menu_id(self):
        name = 'www.'
        action = self.env['ir.actions.client'].create({
            'name': name,
            'tag': 'vuente_iframe_help.iframe',
        })

        return self.env['ir.ui.menu'].create({'name': name,
                                              'action': 'ir.actions.client,%d' % action.id
                                          })

    menu_id = fields.Many2one('ir.ui.menu', string="Menu")
    menu_id_name = fields.Char('Entry')
    menu_id_parent_id = fields.Many2one('ir.ui.menu', 'Group', domain=[('iframe_pages_group', '=', True)], required=True)
    sequence = fields.Integer('Sequence')
    link = fields.Char('Link')

    @api.one
    def update_menu(self):
        if not self.menu_id:
            self.menu_id = self.get_default_menu_id()
        self.menu_id.action.params = {'link':self.link}
        self.menu_id.name = self.menu_id_name
        self.menu_id.action.name = self.menu_id_name
        self.menu_id.parent_id = self.menu_id_parent_id
        self.menu_id.sequence = self.sequence

    @api.model
    def create(self, vals):
        res = super(VuenteIframePage, self).create(vals)
        res.update_menu()
        return res

    @api.multi
    def write(self, vals):
        res = super(VuenteIframePage, self).write(vals)
        self.update_menu()
        return res

    @api.multi
    def unlink(self):
        self.menu_id.unlink()
        return super(VuenteIframePage, self).unlink()
