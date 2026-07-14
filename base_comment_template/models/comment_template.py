# Copyright 2014 Guewen Baconnier (Camptocamp SA)
# Copyright 2013-2014 Nicolas Bessi (Camptocamp SA)
# Copyright 2020 NextERP Romania SRL
# Copyright 2021-2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import markupsafe

from odoo import Command, api, fields, models
from odoo.fields import Domain
from odoo.tools.safe_eval import safe_eval


class CommentTemplate(models.AbstractModel):
    _name = "comment.template"
    _description = (
        "base.comment.template to put header and footer "
        "in reports based on created comment templates"
    )
    # This field allows to set any given field that determines the source partner for
    # the comment templates downstream.
    # E.g.: other models where the partner field is called customer_id.
    _comment_template_partner_field_name = "partner_id"

    comment_template_ids = fields.Many2many(
        compute="_compute_comment_template_ids",
        compute_sudo=True,
        comodel_name="base.comment.template",
        string="Comment Template",
        domain=lambda self: self.env["base.comment.template"]._search_model_ids(
            "in", self._name
        ),
        store=True,
        readonly=False,
    )

    def _get_applicable_comment_template_ids(self):
        """Return partner/global comment templates that match this record."""
        self.ensure_one()
        template_model = self.env["base.comment.template"]
        template_domain = template_model._search_model_ids("in", self._name)
        partner = self[self._comment_template_partner_field_name]
        partner_template_ids = (
            partner.base_comment_template_ids.ids if partner else []
        )
        templates = template_model.search(
            Domain.AND(
                [
                    [
                        "|",
                        ("id", "in", partner_template_ids),
                        ("global_template", "=", True),
                    ],
                    template_domain,
                ]
            )
        )
        applicable = template_model.browse()
        for template in templates:
            domain = safe_eval(template.domain)
            if not domain or self.filtered_domain(domain):
                applicable |= template
        return applicable

    @api.depends(_comment_template_partner_field_name)
    def _compute_comment_template_ids(self):
        partner_field = self._comment_template_partner_field_name
        for record in self:
            applicable = record._get_applicable_comment_template_ids()
            origin = record._origin
            # New records: apply partner/global defaults.
            if not origin or not origin.id:
                record.comment_template_ids = [Command.set(applicable.ids)]
                continue
            # Partner changed: replace with defaults for the new partner.
            if origin[partner_field] != record[partner_field]:
                record.comment_template_ids = [Command.set(applicable.ids)]
                continue
            # Same partner (including spurious recomputes e.g. during print):
            # keep manual selections and still ensure defaults are present.
            record.comment_template_ids = record.comment_template_ids | applicable

    def render_comment(self, comment, engine=False, add_context=None, options=None):
        self.ensure_one()
        comment_texts = self.env["mail.render.mixin"]._render_template(
            template_src=comment.text,
            model=self._name,
            res_ids=[self.id],
            engine=engine or comment.engine,
            add_context=add_context,
            options=options,
        )
        return markupsafe.Markup(comment_texts[self.id]) or ""
