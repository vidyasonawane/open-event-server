from flask_rest_jsonapi import ResourceDetail
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.api.bootstrap import api
from app.models import db
from app.models.user import User
from app.api.data_layers.NoModelLayer import NoModelLayer
from app.models.event import Event
from app.models.users_events_role import UsersEventsRoles
from app.models.role import Role
from app.api.helpers.db import get_count


class AdminStatisticsUserSchema(Schema):
    """
    Api schema
    """
    class Meta:
        """
        Meta class
        """
        type_ = 'admin-statistics-user'
        self_view = 'v1.admin_statistics_user_detail'
        inflect = dasherize

    id = fields.String()
    super_admin = fields.Method("super_admin_count")
    admin = fields.Method("admin_count")
    verified = fields.Method("verified_count")
    unverified = fields.Method("unverified_count")
    organizer = fields.Method("organizer_count")
    coorganizer = fields.Method("coorganizer_count")
    attendee = fields.Method("attendee_count")
    track_organizer = fields.Method("track_organizer_count")

    def super_admin_count(self, obj):
        return get_count(User.query.filter_by(is_super_admin=True))

    def admin_count(self, obj):
        return get_count(User.query.filter_by(is_admin=True, is_super_admin=False))

    def verified_count(self, obj):
        return get_count(User.query.filter_by(is_verified=True, is_super_admin=False, is_admin=False))

    def unverified_count(self, obj):
        return get_count(User.query.filter_by(is_verified=False, is_super_admin=False, is_admin=False))

    def get_all_user_roles(self, role_name):
        role = Role.query.filter_by(name=role_name).first()
        uers = UsersEventsRoles.query.join(UsersEventsRoles.event).join(UsersEventsRoles.role).filter(
            Event.deleted_at.is_(None), UsersEventsRoles.role == role)
        return uers

    def organizer_count(self, obj):
        return get_count(self.get_all_user_roles('organizer'))

    def coorganizer_count(self, obj):
        return get_count(self.get_all_user_roles('coorganizer'))

    def track_organizer_count(self, obj):
        return get_count(self.get_all_user_roles('track_organizer'))

    def attendee_count(self, obj):
        return get_count(self.get_all_user_roles('attendee'))


class AdminStatisticsUserDetail(ResourceDetail):
    """
    Detail by id
    """
    methods = ['GET']
    decorators = (api.has_permission('is_admin'),)
    schema = AdminStatisticsUserSchema
    data_layer = {
        'class': NoModelLayer,
        'session': db.session
    }
