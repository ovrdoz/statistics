from app import db
from datetime import datetime
from sqlalchemy.orm import relationship
from flask.json import JSONEncoder

class HubApi(db.Model):
    __tablename__ = 'hub_api'
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    api_owners = relationship(u'HubOwner', secondary=u'hub_api_has_owner') 
    
    def serialize(self):
        return {
            'id'         : self.id,
            'name'       : self.name,
            'api_owners' : [obj.serialize() for obj in self.api_owners]}  

class HubApplication(db.Model):
    __tablename__ = 'hub_application'
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    
    def serialize(self):
        return {
            'id'   : self.id,
            'name' : self.name }

class HubEntrypoint(db.Model):
    __tablename__ = 'hub_entrypoint'
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    
    def serialize(self):
        return {
            'id'   : self.id,
            'name' : self.name }

class HubOwner(db.Model):
    __tablename__ = 'hub_owner'
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False, server_default=db.text("'undefined'::character varying"))
    
    def serialize(self):
        return {
            'id'   : self.id,
            'name' : self.name }

t_api_has_owner = db.Table(
    'hub_api_has_owner', db.metadata,
    db.Column('api_owner_id', db.ForeignKey(u'hub_owner.id'), primary_key=True, nullable=False),
    db.Column('api_id', db.ForeignKey(u'hub_api.id'), primary_key=True, nullable=False)
)

class HubSummary(db.Model):
    __tablename__ = 'hub_summary'
    id = db.Column(db.BigInteger, primary_key=True)
    application_id = db.Column(db.ForeignKey(u'hub_application.id'), nullable=False)
    application_total = db.Column(db.Integer, nullable=False)
    application_key = db.Column(db.String(255), nullable=False)
    application_key_name = db.Column(db.String(255), nullable=False)
    application_key_total = db.Column(db.Integer, nullable=False)    
    api_id = db.Column(db.ForeignKey(u'hub_api.id'), nullable=False)
    api_total = db.Column(db.Integer, nullable=False)
    resource = db.Column(db.String(255), nullable=False)
    resource_total = db.Column(db.Integer, nullable=False)
    cycle = db.Column(db.DateTime, nullable=False)
    owner_id = db.Column(db.ForeignKey(u'hub_owner.id'), nullable=False, server_default=db.text("1"))
    entrypoint_id = db.Column(db.ForeignKey(u'hub_entrypoint.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.text("now()"))
    api = relationship(u'HubApi')
    application = relationship(u'HubApplication')
    entrypoint = relationship(u'HubEntrypoint')
    owner = relationship(u'HubOwner')
    event_status = relationship(u'HubEventStatus')

    def serialize (self):
        return {
            'id'                    : self.id,
            'application_key'       : self.application_key,
            'application_key_name'  : self.application_key_name,
            'application_key_total' : self.application_key_total,
            'application'           : self.application.serialize(),
            'application_total'     : self.application_total,
            'api'                   : self.api.serialize(),
            'api_total'             : self.api_total,
            'resource'              : self.resource,
            'entrypoint'            : self.entrypoint.serialize(),
            'cycle'                 : self.cycle.strftime("%Y-%m-%dT%H:00:00.000Z"),
            'event_status'          : [obj.serialize() for obj in self.event_status]}  
                
class HubEventStatus(db.Model):
    __tablename__ = 'hub_event_status'
    id = db.Column(db.BigInteger, primary_key=True)
    entrypoint_status_code = db.Column(db.Integer, nullable=False)
    entrypoint_status_total = db.Column(db.Integer, nullable=False)
    entrypoint_time_avg = db.Column(db.Numeric(11, 2), nullable=False)
    endpoint_status_code = db.Column(db.Integer, nullable=False)
    endpoint_status_total = db.Column(db.Integer, nullable=False)
    endpoint_time_avg = db.Column(db.Numeric(11, 2), nullable=False)
    entrypoint_method = db.Column(db.String(10), nullable=False)
    summary_id = db.Column(db.ForeignKey(u'hub_summary.id'), nullable=False)
    summary = relationship(u'HubSummary')

    def serialize(self):
        return {
            'id'                       : self.id,
            'entrypoint_status_code'   : self.entrypoint_status_code,
            'entrypoint_status_total'  : self.entrypoint_status_total,
            'entrypoint_time_avg'      : str(self.entrypoint_time_avg),
            'endpoint_status_code'     : self.endpoint_status_code,
            'endpoint_status_total'    : self.endpoint_status_total,
            'endpoint_time_avg'        : str(self.endpoint_time_avg),
            'entrypoint_method'        : self.entrypoint_method}

#class JSONEncoder(JSONEncoder):
#    def default(self, obj):
#        if isinstance(obj, EqltByGene):
#            return {
#                'gene_id': obj.gene_id, 
#                'gene_symbol': obj.gene_symbol,
#                'p_value': obj.p_value,
#            }
#        return super(MyJSONEncoder, self).default(obj)

#class SuperJSONDecoder(JSONDecoder):
#    def __init__(self, cls, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        self.cls = cls
#    
#    def decode(self, data, object_class):
#        if isinstance(data, str):
#            data = super().decode(data)
#        data = {key, value for key, value in data.items() if not key.endswith("_id")}
#        return object_class(**data)